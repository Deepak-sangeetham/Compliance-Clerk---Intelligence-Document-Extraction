import os
import re
import csv
import shutil
from pathlib import Path
from pypdf import PdfReader, PdfWriter

# Import your existing modules
from src.pdf_extractor import extract_text_from_pdf
from src.ocr_extractor import extract_pdf_with_rest
from src.llm import LLMService

class ExtractionPipeline:
    def __init__(self, input_folder, processed_folder):
        self.input_path = Path(input_folder)
        self.processed_path = Path(processed_folder)
        self.processed_path.mkdir(exist_ok=True)
        self.llm = LLMService()

    def step1_prepare_files(self):
        """Pairs documents and clips Lease Deeds to pages 2-4."""
        pairs = {}
        for pdf in self.input_path.glob("*.pdf"):
            doc_id = re.search(r"(\d+)", pdf.name).group(1)
            if doc_id not in pairs: pairs[doc_id] = {}
            
            if "final" in pdf.name.lower():
                # Copy Final Order as is
                dest = self.processed_path / pdf.name
                shutil.copy(pdf, dest)
                pairs[doc_id]['final'] = dest
            else:
                # Clip Lease Deed (Pages 2-4 -> Index 1 to 3)
                dest = self.processed_path / f"clipped_{pdf.name}"
                reader = PdfReader(pdf)
                writer = PdfWriter()
                for i in range(1, min(4, len(reader.pages))):
                    writer.add_page(reader.pages[i])
                with open(dest, "wb") as f:
                    writer.write(f)
                pairs[doc_id]['lease'] = dest
        return pairs

    def step2_extract_text(self, doc_pair):
        """Extracts text using the appropriate engine for each type."""
        final_text = ""
        lease_text = ""
        
        if 'final' in doc_pair:
            final_text = extract_text_from_pdf(doc_pair['final'])
        if 'lease' in doc_pair:
            lease_text = extract_pdf_with_rest(doc_pair['lease'])
            
        return final_text, lease_text

    def step3_llm_processing(self, doc_id, final_text, lease_text):
        """Loads Markdown prompts and calls LLM to extract data."""
        
        # Define paths to your .md prompt files
        prompt_final_path = Path(r"prompts_db\NA_FinalOrderPrompt.md") 
        prompt_lease_path = Path(r"prompts_db\LeaseDeedPrompt.md")

        # 1. Process Final Order
        data_final = {}
        if final_text and prompt_final_path.exists():
            prompt_final = prompt_final_path.read_text(encoding="utf-8")
            data_final = self.llm.call_llm(prompt_final, final_text, doc_id, "final_order")
        else:
            print(f"Warning: Skipping Final Order for {doc_id} (Text or Prompt missing)")

        # 2. Process Lease Deed
        data_lease = {}
        if lease_text and prompt_lease_path.exists():
            prompt_lease = prompt_lease_path.read_text(encoding="utf-8")
            data_lease = self.llm.call_llm(prompt_lease, lease_text, doc_id, "lease_deed")
        else:
            print(f"Warning: Skipping Lease Deed for {doc_id} (Text or Prompt missing)")

        # Consolidate into one flat dictionary for CSV
        # This merges the two JSON responses into a single row
        return {
            "Survey_ID": doc_id,
            **data_final, 
            **data_lease
        }
    

    def step4_save_to_csv(self, results, output_file="results.csv"):
        if not results: return
        keys = results[0].keys()
        with open(output_file, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)