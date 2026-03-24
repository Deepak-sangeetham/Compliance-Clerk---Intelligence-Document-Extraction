from pathlib import Path
import os
from typing import Dict, List

import fitz

from src.detector import detect_doc_type
from src.pdf_extractor import extract_text_from_pdf

def main():

    file_path = r"Navspark hiring\inputs\255 FINAL ORDER.pdf"

    with fitz.open(file_path) as d:
        page_count = d.page_count
        doc_type = detect_doc_type(page_count)

        # Extract only the first two pages for context (requirement)
        text = extract_text_from_pdf(
            file_path,
            force_ocr=False,
            start_page=0,
            end_page=min(2, page_count),
        )
        # Save the exact input context text for inspection
        
        context_path = Path(r"output.txt")
        context_path.write_text(text,encoding="utf-8")


if __name__ == "__main__":
    main()