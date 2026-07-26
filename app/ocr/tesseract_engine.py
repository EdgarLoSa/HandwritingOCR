from __future__ import annotations

import csv
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OcrCandidate:
    text: str
    confidence: float
    label: str
    config: str


def _tesseract_binary() -> str:
    binary = shutil.which("tesseract")
    if binary:
        return binary
    fallback = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if fallback.exists():
        return str(fallback)
    raise RuntimeError("Tesseract executable not found.")


def _run_tesseract(image_path: Path, output_base: Path, config: str, psm: int) -> tuple[str, float]:
    binary = _tesseract_binary()
    command = [
        binary,
        str(image_path),
        str(output_base),
        "--oem",
        "1",
        "--psm",
        str(psm),
        "-c",
        "user_defined_dpi=300",
        "tsv",
    ]
    command.extend(config.split())
    subprocess.run(command, check=True, capture_output=True, text=True)

    tsv_path = output_base.with_suffix(".tsv")
    text_path = output_base.with_suffix(".txt")

    text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path.exists() else ""
    confidence_values: list[float] = []
    if tsv_path.exists():
        with tsv_path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                conf = row.get("conf", "")
                txt = (row.get("text") or "").strip()
                if txt and conf not in ("", "-1"):
                    try:
                        confidence_values.append(float(conf))
                    except ValueError:
                        continue
    confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    return text.strip(), confidence


def choose_best_result(image_path: Path, work_dir: Path, label: str) -> OcrCandidate:
    configs = [
        "",
        "-c preserve_interword_spaces=1",
        "-c preserve_interword_spaces=1 -c tessedit_char_blacklist=|",
    ]
    psms = [6, 4, 11, 12]
    best = OcrCandidate(text="", confidence=-1.0, label=label, config="")
    for index, config in enumerate(configs):
        for psm in psms:
            base = work_dir / f"{label}_{index}_{psm}"
            text, confidence = _run_tesseract(image_path, base, config, psm)
            if confidence > best.confidence and text.strip():
                best = OcrCandidate(text=text, confidence=confidence, label=label, config=config)
    return best
