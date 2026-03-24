from pathlib import Path
from typing import Optional
import fitz

def extract_text_from_pdf(
    pdf_path: Path,
    force_ocr: bool = False,
    min_text_len: int = 40,
    start_page: int = 0,
    end_page: Optional[int] = None,
) -> str:
    doc = fitz.open(pdf_path)
    parts = []
    total_pages = doc.page_count
    start = max(0, start_page)
    end = min(end_page if end_page is not None else total_pages, total_pages)
    for page_index in range(start, end):
        page = doc[page_index]
        text = page.get_text("text") if not force_ocr else ""
        parts.append(text.strip())
    return "\n\n".join(parts)