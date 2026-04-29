from __future__ import annotations

import os
from pathlib import Path
from time import perf_counter

from ultralytics import YOLO

from ai.models.yolo.cbam import CBAM_MODEL_CFG, register_cbam_with_ultralytics


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_YAML = PROJECT_ROOT / "datasets" / "garbage_single" / "data.yaml"
DEFAULT_MODEL = PROJECT_ROOT / "backend" / "yolov8n.pt"
DEFAULT_RUNS_DIR = PROJECT_ROOT / "runs" / "detect"


# Keep BLAS thread count low to reduce memory pressure on Windows laptops.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")


def train_garbage_detector(
	data_yaml: str | Path = DEFAULT_DATA_YAML,
	model_path: str | Path = DEFAULT_MODEL,
	pretrained_weights: str | Path | None = None,
	epochs: int = 40,
	imgsz: int = 512,
	batch: int = 2,
	device: str | int = "0",
	workers: int = 0,
	project: str | Path = DEFAULT_RUNS_DIR,
	name: str = "garbage_single",
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
	print("[train] loading model...", flush=True)
	register_cbam_with_ultralytics()
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


def train_cbam_garbage_detector(
	data_yaml: str | Path = DEFAULT_DATA_YAML,
	pretrained_weights: str | Path = DEFAULT_MODEL,
	epochs: int = 40,
	imgsz: int = 512,
	batch: int = 2,
	device: str | int = "0",
	workers: int = 0,
	project: str | Path = DEFAULT_RUNS_DIR,
	name: str = "combined_garbage_cbam",
):
	return train_garbage_detector(
		data_yaml=data_yaml,
		model_path=CBAM_MODEL_CFG,
		pretrained_weights=pretrained_weights,
		epochs=epochs,
		imgsz=imgsz,
		batch=batch,
		device=device,
		workers=workers,
		project=project,
		name=name,
	)


if __name__ == "__main__":
	print("[train] script started", flush=True)
	train_garbage_detector()
	print("[train] training finished", flush=True)
