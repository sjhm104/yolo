from __future__ import annotations

import random
import shutil
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DATASET_DIR = Path(
	r"D:\BaiduNetdiskDownload\垃圾数据集\3943f-main\yolo垃圾分类数据集"
)
OUTPUT_DATASET_DIR = PROJECT_ROOT / "datasets" / "garbage_single"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SPLIT_RATIOS = {
	"train": 0.8,
	"val": 0.1,
	"test": 0.1,
}


def _clear_output_dir(output_dir: Path) -> None:
	if output_dir.exists():
		shutil.rmtree(output_dir)


def _ensure_split_dirs(output_dir: Path) -> None:
	for split in SPLIT_RATIOS:
		(output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
		(output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def _iter_samples(source_dir: Path) -> list[tuple[Path, Path]]:
	images_dir = source_dir / "images"
	labels_dir = source_dir / "labels"

	samples: list[tuple[Path, Path]] = []
	for image_path in images_dir.iterdir():
		if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
			continue
		label_path = labels_dir / f"{image_path.stem}.txt"
		if not label_path.exists():
			continue
		samples.append((image_path, label_path))
	return samples


def _single_class_lines(label_path: Path) -> list[str]:
	lines: list[str] = []
	for raw_line in label_path.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line:
			continue
		parts = line.split()
		if len(parts) != 5:
			continue
		lines.append(f"0 {' '.join(parts[1:])}")
	return lines


def _split_counts(total: int) -> dict[str, int]:
	train_count = int(total * SPLIT_RATIOS["train"])
	val_count = int(total * SPLIT_RATIOS["val"])
	test_count = total - train_count - val_count
	return {
		"train": train_count,
		"val": val_count,
		"test": test_count,
	}


def _write_data_yaml(output_dir: Path) -> None:
	content = "\n".join(
		[
			f"path: {output_dir.as_posix()}",
			"train: images/train",
			"val: images/val",
			"test: images/test",
			"",
			"names:",
			"  0: garbage",
			"",
		]
	)
	(output_dir / "data.yaml").write_text(content, encoding="utf-8")


def prepare_single_class_dataset(
	source_dir: Path = SOURCE_DATASET_DIR,
	output_dir: Path = OUTPUT_DATASET_DIR,
	seed: int = 42,
) -> dict[str, int]:
	if not source_dir.exists():
		raise FileNotFoundError(f"源数据集不存在: {source_dir}")

	samples = _iter_samples(source_dir)
	if not samples:
		raise ValueError("未找到可用的图片-标签配对数据")

	random.Random(seed).shuffle(samples)
	counts = _split_counts(len(samples))

	_clear_output_dir(output_dir)
	_ensure_split_dirs(output_dir)

	split_names: list[str] = (
		["train"] * counts["train"]
		+ ["val"] * counts["val"]
		+ ["test"] * counts["test"]
	)

	class_counter: Counter[str] = Counter()
	for (image_path, label_path), split in zip(samples, split_names, strict=True):
		target_image = output_dir / "images" / split / image_path.name
		target_label = output_dir / "labels" / split / label_path.name

		shutil.copy2(image_path, target_image)
		lines = _single_class_lines(label_path)
		target_label.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
		class_counter[split] += 1

	_write_data_yaml(output_dir)

	return {
		"total": len(samples),
		"train": class_counter["train"],
		"val": class_counter["val"],
		"test": class_counter["test"],
	}


if __name__ == "__main__":
	summary = prepare_single_class_dataset()
	print(summary)
