from __future__ import annotations

from pathlib import Path

from docx import Document


def write_text_export(output_dir: Path, filename: str, text: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{Path(filename).stem}.txt"
    output_path.write_text(text, encoding="utf-8")
    return output_path


def write_docx_export(output_dir: Path, filename: str, text: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{Path(filename).stem}.docx"
    document = Document()
    for paragraph in text.splitlines() or [""]:
        document.add_paragraph(paragraph)
    document.save(output_path)
    return output_path
