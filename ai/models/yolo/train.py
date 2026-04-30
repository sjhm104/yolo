from __future__ import annotations

import argparse
import os
from pathlib import Path
from time import perf_counter

from ultralytics import YOLO

from ai.models.yolo.p2_eiou import P2_MODEL_CFG, register_eiou_loss_with_ultralytics


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_YAML = PROJECT_ROOT / "datasets" / "uav_waste_single" / "data.yaml"
DEFAULT_MODEL = PROJECT_ROOT / "yolo26n.pt"
DEFAULT_RUNS_DIR = PROJECT_ROOT / "runs" / "detect"


# Keep BLAS thread count low to reduce memory pressure on Windows laptops.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")


def _pick_default_pretrained() -> Path:
	runs_dir = PROJECT_ROOT / "runs" / "detect"
	patterns = [
		"uav_waste_p2_eiou*/weights/best.pt",
		"train-2/weights/best.pt",
		"garbage_single*/weights/best.pt",
		"uav_waste_single*/weights/best.pt",
	]
	for pattern in patterns:
		candidates = sorted(runs_dir.glob(pattern), key=lambda path: path.stat().st_mtime, reverse=True)
		for candidate in candidates:
			if candidate.exists():
				return candidate
	return DEFAULT_MODEL


def _validate_training_inputs(
	data_yaml: str | Path,
	model_path: str | Path,
	pretrained_weights: str | Path | None,
) -> None:
	data_yaml = Path(data_yaml)
	model_path = Path(model_path)
	if not data_yaml.exists():
		raise FileNotFoundError(f"Dataset YAML not found: {data_yaml}")
	if not model_path.exists():
		raise FileNotFoundError(f"Model YAML or weight file not found: {model_path}")
	if pretrained_weights is not None and not Path(pretrained_weights).exists():
		raise FileNotFoundError(f"Pretrained weights not found: {pretrained_weights}")


def train_garbage_detector(
	data_yaml: str | Path = DEFAULT_DATA_YAML,
	model_path: str | Path = DEFAULT_MODEL,
	pretrained_weights: str | Path | None = None,
	epochs: int = 100,
	imgsz: int = 640,
	batch: int = 16,
	device: str | int = "0",
	workers: int = 8,
	project: str | Path = DEFAULT_RUNS_DIR,
	name: str = "uav_waste_p2_eiou",
):
	started_at = perf_counter()
	print("[train] project_root =", PROJECT_ROOT, flush=True)
	print("[train] data_yaml =", data_yaml, flush=True)
	print("[train] model_path =", model_path, flush=True)
	print("[train] pretrained_weights =", pretrained_weights, flush=True)
	print("[train] device =", device, flush=True)
	print("[train] imgsz =", imgsz, flush=True)
	print("[train] batch =", batch, flush=True)
	print("[train] workers =", workers, flush=True)
	_validate_training_inputs(data_yaml, model_path, pretrained_weights)
	print("[train] loading model...", flush=True)
	register_eiou_loss_with_ultralytics()
	model = YOLO(str(model_path))
	if pretrained_weights:
		print("[train] loading pretrained weights...", flush=True)
		model = model.load(str(pretrained_weights))
	print("[train] model loaded, starting training...", flush=True)
	result = model.train(
		data=str(data_yaml),
		epochs=epochs,
		imgsz=imgsz,
		batch=batch,
		device=device,
		workers=workers,
		project=str(project),
		name=name,
		verbose=True,
	)
	print(f"[train] finished in {perf_counter() - started_at:.1f}s", flush=True)
	return result


def train_p2_eiou_garbage_detector(
	data_yaml: str | Path = DEFAULT_DATA_YAML,
	pretrained_weights: str | Path = _pick_default_pretrained(),
	epochs: int = 100,
	imgsz: int = 640,
	batch: int = 16,
	device: str | int = "0",
	workers: int = 8,
	project: str | Path = DEFAULT_RUNS_DIR,
	name: str = "uav_waste_p2_eiou",
):
	return train_garbage_detector(
		data_yaml=data_yaml,
		model_path=P2_MODEL_CFG,
		pretrained_weights=pretrained_weights,
		epochs=epochs,
		imgsz=imgsz,
		batch=batch,
		device=device,
		workers=workers,
		project=project,
		name=name,
	)


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Train YOLOv8n + P2 + EIoU on the UAV waste dataset.")
	parser.add_argument("--data", default=str(DEFAULT_DATA_YAML), help="Path to dataset YAML.")
	parser.add_argument(
		"--pretrained",
		default=str(_pick_default_pretrained()),
		help="Path to pretrained weights. Defaults to the most recent local best.pt if available.",
	)
	parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs.")
	parser.add_argument("--imgsz", type=int, default=640, help="Training image size.")
	parser.add_argument("--batch", type=int, default=16, help="Batch size.")
	parser.add_argument("--device", default="0", help="CUDA device id or cpu.")
	parser.add_argument("--workers", type=int, default=8, help="Number of dataloader workers.")
	parser.add_argument("--project", default=str(DEFAULT_RUNS_DIR), help="Runs output directory.")
	parser.add_argument("--name", default="uav_waste_p2_eiou", help="Run name.")
	return parser.parse_args()


if __name__ == "__main__":
	print("[train] script started", flush=True)
	args = parse_args()
	train_p2_eiou_garbage_detector(
		data_yaml=args.data,
		pretrained_weights=args.pretrained,
		epochs=args.epochs,
		imgsz=args.imgsz,
		batch=args.batch,
		device=args.device,
		workers=args.workers,
		project=args.project,
		name=args.name,
	)
	print("[train] training finished", flush=True)
