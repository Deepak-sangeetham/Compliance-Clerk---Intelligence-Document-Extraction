from pathlib import Path
import os
from typing import Dict, List
import re
import fitz

from src.pdf_extractor import extract_text_from_pdf
from src.ocr_extractor import extract_pdf_with_rest
from src.llm import LLMService 

def main():

    file_path = r"257_extracted.pdf"
    lease_text = extract_pdf_with_rest(file_path)

    llm_service = LLMService()

    doc_id = re.search(r"(\d+)", file_path).group(1)

    file_path = r"Navspark hiring\inputs\257 FINAL ORDER.pdf"
    with fitz.open(file_path) as d:
        page_count = d.page_count

    
    final_text = extract_text_from_pdf(
            file_path,
            force_ocr=False,
            start_page=0,
            end_page=min(2, page_count),
        )
    prompt_final_path = Path(r"prompts_db\NA_FinalOrderPrompt.md")
    prompt_lease_path = Path(r"prompts_db\LeaseDeedPrompt.md")

    # 1. Process Final Order

    print(final_text)
    print(lease_text)
    data_final = {}
    if final_text and prompt_final_path.exists():
        prompt_final = prompt_final_path.read_text(encoding="utf-8")
        data_final = llm_service.call_llm(prompt_final, context_text=final_text)
    else:
        print(f"Warning: Skipping Final Order for {doc_id} (Text or Prompt missing)")

    # 2. Process Lease Deed
    data_lease = {}
    if lease_text and prompt_lease_path.exists():
        prompt_lease = prompt_lease_path.read_text(encoding="utf-8")
        data_lease = llm_service.call_llm(prompt_lease, context_text=lease_text)
    else:
        print(f"Warning: Skipping Lease Deed for {doc_id} (Text or Prompt missing)")


if __name__ == "__main__":
    main()