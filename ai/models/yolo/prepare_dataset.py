from __future__ import annotations

import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_GARBAGE_DIR = Path(
	r"D:\BaiduNetdiskDownload\垃圾数据集\3943f-main\yolo垃圾分类数据集"
)
OUTPUT_GARBAGE_DIR = PROJECT_ROOT / "datasets" / "garbage_single"

SOURCE_UAV_WASTE_DIR = Path(
	r"D:\BaiduNetdiskDownload\垃圾数据集\KY005：无人机环境垃圾检测数据集UAVVaste"
)
OUTPUT_UAV_WASTE_DIR = PROJECT_ROOT / "datasets" / "uav_waste_single"
OUTPUT_COMBINED_DIR = PROJECT_ROOT / "datasets" / "combined_garbage"

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
	for split in ("train", "val", "test"):
		(output_dir / "images" / split).mkdir(parents=True, exist_ok=True)
		(output_dir / "labels" / split).mkdir(parents=True, exist_ok=True)


def _write_data_yaml(output_dir: Path, class_name: str = "garbage") -> None:
	content = "\n".join(
		[
			f"path: {output_dir.as_posix()}",
			"train: images/train",
			"val: images/val",
			"test: images/test",
			"",
			"names:",
			f"  0: {class_name}",
			"",
		]
	)
	(output_dir / "data.yaml").write_text(content, encoding="utf-8")


def _split_counts(total: int) -> dict[str, int]:
	train_count = int(total * SPLIT_RATIOS["train"])
	val_count = int(total * SPLIT_RATIOS["val"])
	test_count = total - train_count - val_count
	return {
		"train": train_count,
		"val": val_count,
		"test": test_count,
	}


def _prepare_original_single_class_dataset(
	source_dir: Path,
	output_dir: Path,
	seed: int = 42,
) -> dict[str, int]:
	images_dir = source_dir / "images"
	labels_dir = source_dir / "labels"
	if not images_dir.exists() or not labels_dir.exists():
		raise FileNotFoundError(f"原始 YOLO 数据集结构不完整: {source_dir}")

	samples: list[tuple[Path, Path]] = []
	for image_path in images_dir.iterdir():
		if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
			continue
		label_path = labels_dir / f"{image_path.stem}.txt"
		if label_path.exists():
			samples.append((image_path, label_path))

	if not samples:
		raise ValueError("未找到可用的图片-标签配对数据")

	random.Random(seed).shuffle(samples)
	counts = _split_counts(len(samples))
	split_names = (
		["train"] * counts["train"]
		+ ["val"] * counts["val"]
		+ ["test"] * counts["test"]
	)

	_clear_output_dir(output_dir)
	_ensure_split_dirs(output_dir)

	split_counter: Counter[str] = Counter()
	for (image_path, label_path), split in zip(samples, split_names, strict=True):
		target_image = output_dir / "images" / split / image_path.name
		target_label = output_dir / "labels" / split / label_path.name

		shutil.copy2(image_path, target_image)

		lines: list[str] = []
		for raw_line in label_path.read_text(encoding="utf-8").splitlines():
			line = raw_line.strip()
			if not line:
				continue
			parts = line.split()
			if len(parts) == 5:
				lines.append(f"0 {' '.join(parts[1:])}")

		target_label.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
		split_counter[split] += 1

	_write_data_yaml(output_dir)
	return {
		"total": len(samples),
		"train": split_counter["train"],
		"val": split_counter["val"],
		"test": split_counter["test"],
	}


def _load_uav_split_map(split_file: Path) -> dict[str, str]:
	if not split_file.exists():
		raise FileNotFoundError(f"UAV 数据集划分文件不存在: {split_file}")

	data = json.loads(split_file.read_text(encoding="utf-8"))
	split_map: dict[str, str] = {}
	for split_name in ("train", "val", "test"):
		for file_name in data.get(split_name, []):
			split_map[str(file_name)] = split_name
	return split_map


def _normalize_bbox(
	bbox: list[float],
	width: float,
	height: float,
) -> tuple[float, float, float, float] | None:
	if len(bbox) != 4 or width <= 0 or height <= 0:
		return None

	x, y, box_w, box_h = [float(value) for value in bbox]
	if box_w <= 0 or box_h <= 0:
		return None

	x_center = (x + box_w / 2.0) / width
	y_center = (y + box_h / 2.0) / height
	norm_w = box_w / width
	norm_h = box_h / height

	if not (0.0 <= x_center <= 1.0 and 0.0 <= y_center <= 1.0):
		return None
	if not (0.0 < norm_w <= 1.0 and 0.0 < norm_h <= 1.0):
		return None

	return (x_center, y_center, norm_w, norm_h)


def prepare_uav_waste_dataset(
	source_dir: Path = SOURCE_UAV_WASTE_DIR,
	output_dir: Path = OUTPUT_UAV_WASTE_DIR,
) -> dict[str, int]:
	annotations_file = source_dir / "annotations" / "annotations.json"
	split_file = source_dir / "annotations" / "train_val_test_distribution_file.json"
	images_dir = source_dir / "images"

	if not annotations_file.exists():
		raise FileNotFoundError(f"UAV 标注文件不存在: {annotations_file}")
	if not images_dir.exists():
		raise FileNotFoundError(f"UAV 图片目录不存在: {images_dir}")

	split_map = _load_uav_split_map(split_file)
	coco = json.loads(annotations_file.read_text(encoding="utf-8"))

	image_items = coco.get("images", [])
	annotation_items = coco.get("annotations", [])

	images_by_id = {int(item["id"]): item for item in image_items}
	annotations_by_image_id: dict[int, list[dict]] = defaultdict(list)
	for annotation in annotation_items:
		annotations_by_image_id[int(annotation["image_id"])].append(annotation)

	_clear_output_dir(output_dir)
	_ensure_split_dirs(output_dir)

	split_counter: Counter[str] = Counter()
	annotation_counter = 0
	skipped_images = 0

	for image_id, image_info in images_by_id.items():
		file_name = str(image_info["file_name"])
		split = split_map.get(file_name)
		if split not in {"train", "val", "test"}:
			skipped_images += 1
			continue

		source_image = images_dir / file_name
		if not source_image.exists():
			skipped_images += 1
			continue

		width = float(image_info.get("width", 0))
		height = float(image_info.get("height", 0))
		target_image = output_dir / "images" / split / source_image.name
		target_label = output_dir / "labels" / split / f"{source_image.stem}.txt"
		shutil.copy2(source_image, target_image)

		lines: list[str] = []
		for annotation in annotations_by_image_id.get(image_id, []):
			normalized = _normalize_bbox(annotation.get("bbox", []), width, height)
			if normalized is None:
				continue
			x_center, y_center, box_w, box_h = normalized
			lines.append(f"0 {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}")
			annotation_counter += 1

		target_label.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
		split_counter[split] += 1

	_write_data_yaml(output_dir, class_name="garbage")
	return {
		"total": sum(split_counter.values()),
		"train": split_counter["train"],
		"val": split_counter["val"],
		"test": split_counter["test"],
		"annotations": annotation_counter,
		"skipped_images": skipped_images,
	}


def prepare_single_class_dataset(
	source_dir: Path = SOURCE_GARBAGE_DIR,
	output_dir: Path = OUTPUT_GARBAGE_DIR,
	seed: int = 42,
) -> dict[str, int]:
	return _prepare_original_single_class_dataset(source_dir, output_dir, seed=seed)


def prepare_combined_garbage_dataset(
	original_dir: Path = OUTPUT_GARBAGE_DIR,
	uav_dir: Path = OUTPUT_UAV_WASTE_DIR,
	output_dir: Path = OUTPUT_COMBINED_DIR,
) -> dict[str, int]:
	if not (original_dir / "data.yaml").exists():
		raise FileNotFoundError(f"原始垃圾单类数据集尚未准备: {original_dir}")
	if not (uav_dir / "data.yaml").exists():
		raise FileNotFoundError(f"UAV 垃圾单类数据集尚未准备: {uav_dir}")

	_clear_output_dir(output_dir)
	_ensure_split_dirs(output_dir)

	summary: Counter[str] = Counter()
	for dataset_name, dataset_dir in (
		("ground", original_dir),
		("uav", uav_dir),
	):
		for split in ("train", "val", "test"):
			source_images_dir = dataset_dir / "images" / split
			source_labels_dir = dataset_dir / "labels" / split
			target_images_dir = output_dir / "images" / split
			target_labels_dir = output_dir / "labels" / split

			for image_path in source_images_dir.iterdir():
				if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
					continue
				label_path = source_labels_dir / f"{image_path.stem}.txt"
				if not label_path.exists():
					continue

				target_stem = f"{dataset_name}_{image_path.stem}"
				target_image = target_images_dir / f"{target_stem}{image_path.suffix.lower()}"
				target_label = target_labels_dir / f"{target_stem}.txt"
				shutil.copy2(image_path, target_image)
				shutil.copy2(label_path, target_label)
				summary[split] += 1

	_write_data_yaml(output_dir, class_name="garbage")
	return {
		"total": summary["train"] + summary["val"] + summary["test"],
		"train": summary["train"],
		"val": summary["val"],
		"test": summary["test"],
	}


if __name__ == "__main__":
	print("[prepare] original garbage dataset")
	print(prepare_single_class_dataset())
	print("[prepare] uav waste dataset")
	print(prepare_uav_waste_dataset())
	print("[prepare] combined garbage dataset")
	print(prepare_combined_garbage_dataset())
