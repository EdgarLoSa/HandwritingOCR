from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class PreprocessedImage:
    path: Path
    label: str


def _load_grayscale(image_path: Path) -> np.ndarray:
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    return image


def _normalize(image: np.ndarray) -> np.ndarray:
    return cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)


def _deskew(image: np.ndarray) -> np.ndarray:
    coords = np.column_stack(np.where(image < 255))
    if len(coords) < 50:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (height, width) = image.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, matrix, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def build_variants(image_path: Path, work_dir: Path) -> list[PreprocessedImage]:
    work_dir.mkdir(parents=True, exist_ok=True)
    source = _load_grayscale(image_path)
    source = _normalize(source)
    source = _deskew(source)

    variants: list[tuple[str, np.ndarray]] = [
        ("original", source),
        ("otsu", cv2.threshold(cv2.GaussianBlur(source, (3, 3), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
        ("adaptive", cv2.adaptiveThreshold(source, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)),
    ]

    results: list[PreprocessedImage] = []
    for label, variant in variants:
        path = work_dir / f"{label}.png"
        cv2.imwrite(str(path), variant)
        results.append(PreprocessedImage(path=path, label=label))
    return results

