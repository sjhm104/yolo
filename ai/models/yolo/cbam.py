from __future__ import annotations

from pathlib import Path

import torch
from torch import nn


class ChannelAttention(nn.Module):
	"""Channel attention used by CBAM."""

	def __init__(self, channels: int, reduction: int = 16) -> None:
		super().__init__()
		reduced_channels = max(1, channels // reduction)
		self.avg_pool = nn.AdaptiveAvgPool2d(1)
		self.max_pool = nn.AdaptiveMaxPool2d(1)
		self.mlp = nn.Sequential(
			nn.Conv2d(channels, reduced_channels, kernel_size=1, bias=False),
			nn.ReLU(inplace=True),
			nn.Conv2d(reduced_channels, channels, kernel_size=1, bias=False),
		)
		self.activation = nn.Sigmoid()

	def forward(self, x: torch.Tensor) -> torch.Tensor:
		avg_out = self.mlp(self.avg_pool(x))
		max_out = self.mlp(self.max_pool(x))
		return self.activation(avg_out + max_out)


class SpatialAttention(nn.Module):
	"""Spatial attention used by CBAM."""

	def __init__(self, kernel_size: int = 7) -> None:
		super().__init__()
		if kernel_size not in {3, 7}:
			raise ValueError("SpatialAttention kernel_size must be 3 or 7")
		padding = 3 if kernel_size == 7 else 1
		self.conv = nn.Conv2d(2, 1, kernel_size=kernel_size, padding=padding, bias=False)
		self.activation = nn.Sigmoid()

	def forward(self, x: torch.Tensor) -> torch.Tensor:
		avg_out = torch.mean(x, dim=1, keepdim=True)
		max_out, _ = torch.max(x, dim=1, keepdim=True)
		attention = torch.cat([avg_out, max_out], dim=1)
		return self.activation(self.conv(attention))


class CBAM(nn.Module):
	"""Convolutional Block Attention Module."""

	def __init__(self, channels: int, reduction: int = 16, kernel_size: int = 7) -> None:
		super().__init__()
		self.channel_attention = ChannelAttention(channels, reduction=reduction)
		self.spatial_attention = SpatialAttention(kernel_size=kernel_size)

	def forward(self, x: torch.Tensor) -> torch.Tensor:
		x = self.channel_attention(x) * x
		x = self.spatial_attention(x) * x
		return x


def register_cbam_with_ultralytics() -> None:
	"""Register CBAM into Ultralytics task globals so YAML parsing can resolve it."""
	import ultralytics.nn.tasks as tasks

	if getattr(tasks, "CBAM", None) is not CBAM:
		tasks.CBAM = CBAM


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CBAM_MODEL_CFG = PROJECT_ROOT / "ai" / "models" / "yolo" / "yolov8n_cbam.yaml"
