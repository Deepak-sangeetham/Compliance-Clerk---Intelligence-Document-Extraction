from src.pipeline import ExtractionPipeline

def main():
    # Configuration
    INPUT_DIR = r"Navspark hiring\test_inputs"
    PROCESSED_DIR = "processed"
    
    pipeline = ExtractionPipeline(INPUT_DIR, PROCESSED_DIR)
    
    print("Step 1: Preparing and clipping files...")
    document_pairs = pipeline.step1_prepare_files()
    
    all_extracted_data = []

    for doc_id, paths in document_pairs.items():
        print(f"Processing ID {doc_id}...")
        
        # Step 2: Extraction
        final_txt, lease_txt = pipeline.step2_extract_text(paths)
        
        # Step 3: LLM Data Points
        combined_data = pipeline.step3_llm_processing(doc_id, final_txt, lease_txt)
        all_extracted_data.append(combined_data)

    # Step 4: Consolidate
    print("Step 4: Saving results to CSV...")
    pipeline.step4_save_to_csv(all_extracted_data)
    print("Done! Check results.csv and audit_log.jsonl")

if __name__ == "__main__":
    main()