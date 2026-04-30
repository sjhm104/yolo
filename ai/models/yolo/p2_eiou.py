from __future__ import annotations

from pathlib import Path

import torch
import torch.nn.functional as F

import ultralytics.nn.tasks as tasks
import ultralytics.utils.loss as loss_mod
from ultralytics.utils.tal import bbox2dist


def _eiou_term(pred_bboxes: torch.Tensor, target_bboxes: torch.Tensor, eps: float = 1e-7) -> torch.Tensor:
	"""Compute Efficient IoU loss terms for xyxy boxes."""
	px1, py1, px2, py2 = pred_bboxes.unbind(-1)
	tx1, ty1, tx2, ty2 = target_bboxes.unbind(-1)

	inter_x1 = torch.max(px1, tx1)
	inter_y1 = torch.max(py1, ty1)
	inter_x2 = torch.min(px2, tx2)
	inter_y2 = torch.min(py2, ty2)
	inter_w = (inter_x2 - inter_x1).clamp(min=0)
	inter_h = (inter_y2 - inter_y1).clamp(min=0)
	inter_area = inter_w * inter_h

	pred_w = (px2 - px1).clamp(min=eps)
	pred_h = (py2 - py1).clamp(min=eps)
	target_w = (tx2 - tx1).clamp(min=eps)
	target_h = (ty2 - ty1).clamp(min=eps)
	pred_area = pred_w * pred_h
	target_area = target_w * target_h
	union_area = pred_area + target_area - inter_area + eps
	iou = inter_area / union_area

	pred_cx = (px1 + px2) * 0.5
	pred_cy = (py1 + py2) * 0.5
	target_cx = (tx1 + tx2) * 0.5
	target_cy = (ty1 + ty2) * 0.5

	cw = (torch.max(px2, tx2) - torch.min(px1, tx1)).clamp(min=eps)
	ch = (torch.max(py2, ty2) - torch.min(py1, ty1)).clamp(min=eps)
	center_distance = (pred_cx - target_cx).pow(2) + (pred_cy - target_cy).pow(2)
	convex_diag = cw.pow(2) + ch.pow(2) + eps

	width_penalty = (pred_w - target_w).pow(2) / (cw.pow(2) + eps)
	height_penalty = (pred_h - target_h).pow(2) / (ch.pow(2) + eps)
	return 1.0 - iou + center_distance / convex_diag + width_penalty + height_penalty


class EIoUBboxLoss(loss_mod.BboxLoss):
	"""Bounding box loss that replaces CIoU with EIoU for more explicit size regression."""

	def forward(
		self,
		pred_dist: torch.Tensor,
		pred_bboxes: torch.Tensor,
		anchor_points: torch.Tensor,
		target_bboxes: torch.Tensor,
		target_scores: torch.Tensor,
		target_scores_sum: torch.Tensor,
		fg_mask: torch.Tensor,
		imgsz: torch.Tensor,
		stride: torch.Tensor,
	) -> tuple[torch.Tensor, torch.Tensor]:
		weight = target_scores.sum(-1)[fg_mask].unsqueeze(-1)
		eiou = _eiou_term(pred_bboxes[fg_mask], target_bboxes[fg_mask]).unsqueeze(-1)
		loss_iou = (eiou * weight).sum() / target_scores_sum

		if self.dfl_loss:
			target_ltrb = bbox2dist(anchor_points, target_bboxes, self.dfl_loss.reg_max - 1)
			loss_dfl = self.dfl_loss(pred_dist[fg_mask].view(-1, self.dfl_loss.reg_max), target_ltrb[fg_mask]) * weight
			loss_dfl = loss_dfl.sum() / target_scores_sum
		else:
			target_ltrb = bbox2dist(anchor_points, target_bboxes)
			target_ltrb = target_ltrb * stride
			target_ltrb[..., 0::2] /= imgsz[1]
			target_ltrb[..., 1::2] /= imgsz[0]
			pred_dist = pred_dist * stride
			pred_dist[..., 0::2] /= imgsz[1]
			pred_dist[..., 1::2] /= imgsz[0]
			loss_dfl = F.l1_loss(pred_dist[fg_mask], target_ltrb[fg_mask], reduction="none").mean(-1, keepdim=True) * weight
			loss_dfl = loss_dfl.sum() / target_scores_sum

		return loss_iou, loss_dfl


class EIoUv8DetectionLoss(loss_mod.v8DetectionLoss):
	"""Ultralytics v8 detection loss with EIoU box regression."""

	def __init__(self, model, tal_topk: int = 10, tal_topk2: int | None = None):
		super().__init__(model, tal_topk=tal_topk, tal_topk2=tal_topk2)
		self.bbox_loss = EIoUBboxLoss(self.reg_max).to(self.device)


def register_eiou_loss_with_ultralytics() -> None:
	"""Patch Ultralytics so DetectionModel uses the custom EIoU criterion."""
	if getattr(tasks, "EIoUv8DetectionLoss", None) is not EIoUv8DetectionLoss:
		tasks.EIoUv8DetectionLoss = EIoUv8DetectionLoss
	if getattr(tasks, "v8DetectionLoss", None) is not EIoUv8DetectionLoss:
		tasks.v8DetectionLoss = EIoUv8DetectionLoss
	if getattr(loss_mod, "v8DetectionLoss", None) is not EIoUv8DetectionLoss:
		loss_mod.v8DetectionLoss = EIoUv8DetectionLoss


PROJECT_ROOT = Path(__file__).resolve().parents[3]
P2_MODEL_CFG = PROJECT_ROOT / "ai" / "models" / "yolo" / "yolov8n_p2.yaml"
