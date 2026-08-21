from pathlib import Path

from pypdf import PdfReader


def parse_resume(pdf_path: Path) -> dict:
    if not pdf_path.exists():
        return {
            "status": "failed",
            "text": "",
            "pages": 0,
            "error": "Resume file not found.",
        }

    try:
        reader = PdfReader(pdf_path)

        page_text = []

        for page in reader.pages:
            text = page.extract_text() or ""

            if text.strip():
                page_text.append(text.strip())

        full_text = "\n".join(page_text).strip()

        if not full_text:
            return {
                "status": "failed",
                "text": "",
                "pages": len(reader.pages),
                "error": "No readable text found.",
            }

        return {
            "status": "success",
            "text": full_text,
            "pages": len(reader.pages),
            "error": None,
        }

    except Exception as exc:
        return {
            "status": "failed",
            "text": "",
            "pages": 0,
            "error": str(exc),
        }