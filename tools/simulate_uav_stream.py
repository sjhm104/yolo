from __future__ import annotations

import argparse
import itertools
import json
import mimetypes
import time
from pathlib import Path
from typing import Iterator
from urllib import error, request


SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="模拟无人机定时上传图片到检测接口",
	)
	parser.add_argument(
		"--image-dir",
		required=True,
		type=Path,
		help="本地图片目录",
	)
	parser.add_argument(
		"--interval",
		type=float,
		default=3.0,
		help="上传间隔（秒），默认 3",
	)
	parser.add_argument(
		"--drone-id",
		type=int,
		default=1,
		help="无人机 ID，默认 1",
	)
	parser.add_argument(
		"--lat",
		type=float,
		default=31.2304,
		help="纬度，默认 31.2304",
	)
	parser.add_argument(
		"--lng",
		type=float,
		default=121.4737,
		help="经度，默认 121.4737",
	)
	parser.add_argument(
		"--api-url",
		type=str,
		default="http://127.0.0.1:8000/api/v1/detections/upload",
		help="检测上传接口 URL",
	)
	return parser.parse_args()


def iter_images(image_dir: Path) -> Iterator[Path]:
	if not image_dir.exists() or not image_dir.is_dir():
		raise ValueError(f"图片目录不存在: {image_dir}")

	images = sorted(
		path
		for path in image_dir.iterdir()
		if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
	)
	if not images:
		raise ValueError(f"目录中没有可用图片: {image_dir}")

	return itertools.cycle(images)


def build_multipart_body(
	file_path: Path,
	drone_id: int,
	latitude: float,
	longitude: float,
	boundary: str,
) -> bytes:
	content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
	line_break = b"\r\n"
	body = bytearray()

	def add_field(name: str, value: str) -> None:
		body.extend(f"--{boundary}".encode("utf-8"))
		body.extend(line_break)
		body.extend(f'Content-Disposition: form-data; name="{name}"'.encode("utf-8"))
		body.extend(line_break)
		body.extend(line_break)
		body.extend(value.encode("utf-8"))
		body.extend(line_break)

	add_field("drone_id", str(drone_id))
	add_field("latitude", str(latitude))
	add_field("longitude", str(longitude))

	body.extend(f"--{boundary}".encode("utf-8"))
	body.extend(line_break)
	body.extend(
		f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"'.encode("utf-8")
	)
	body.extend(line_break)
	body.extend(f"Content-Type: {content_type}".encode("utf-8"))
	body.extend(line_break)
	body.extend(line_break)
	body.extend(file_path.read_bytes())
	body.extend(line_break)
	body.extend(f"--{boundary}--".encode("utf-8"))
	body.extend(line_break)

	return bytes(body)


def upload_image(
	api_url: str,
	image_path: Path,
	drone_id: int,
	latitude: float,
	longitude: float,
) -> dict:
	boundary = f"----UAVBoundary{int(time.time() * 1000)}"
	body = build_multipart_body(image_path, drone_id, latitude, longitude, boundary)
	headers = {
		"Content-Type": f"multipart/form-data; boundary={boundary}",
	}
	req = request.Request(api_url, data=body, headers=headers, method="POST")

	with request.urlopen(req, timeout=30) as resp:
		payload = resp.read().decode("utf-8")
		return json.loads(payload)


def main() -> None:
	args = parse_args()
	image_iterator = iter_images(args.image_dir)

	print("[UAV] 模拟开始，按 Ctrl+C 停止")
	print(f"[UAV] 图片目录: {args.image_dir}")
	print(f"[UAV] 上传接口: {args.api_url}")
	print(f"[UAV] 上传间隔: {args.interval:.2f}s")

	index = 0
	try:
		for image_path in image_iterator:
			index += 1
			try:
				result = upload_image(
					api_url=args.api_url,
					image_path=image_path,
					drone_id=args.drone_id,
					latitude=args.lat,
					longitude=args.lng,
				)

				has_waste = bool(result.get("has_waste", False))
				confidence = float(result.get("confidence") or 0.0)
				task_created = has_waste

				print(
					f"[UAV][{index}] {image_path.name} 上传成功 | "
					f"has_waste={has_waste} | confidence={confidence:.4f} | "
					f"cleaning_task_created={task_created}"
				)
			except error.HTTPError as exc:
				err_text = exc.read().decode("utf-8", errors="ignore")
				print(f"[UAV][{index}] 上传失败 HTTP {exc.code}: {err_text}")
			except error.URLError as exc:
				print(f"[UAV][{index}] 网络错误: {exc.reason}")
			except Exception as exc:  # noqa: BLE001
				print(f"[UAV][{index}] 未知错误: {exc}")

			time.sleep(max(0.0, args.interval))
	except KeyboardInterrupt:
		print("\n[UAV] 模拟已停止")


if __name__ == "__main__":
	main()
