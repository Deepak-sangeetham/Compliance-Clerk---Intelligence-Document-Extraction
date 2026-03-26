# ComplianceClerk: Intelligent Document Extraction 📑

An automated pipeline designed to extract legal and land data points from disparate document types (NA Final Orders and Lease Deeds) using **Gemini 2.5 Flash** and **PyMuPDF**.

## 🎯 Task Description
The project automates the extraction of 8 critical data points from two different PDF sources related by a common ID or Survey Number:

1.  **From Final Order PDFs (Selectable Text):**
    * Area in NA Order
    * NA Order No.
    * Dated
2.  **From Lease Deed Documents (Scanned/OCR):**
    * Village Name
    * Survey No.
    * Lease Area
    * Lease Deed Doc. No.
    * Lease Start Date

## 💡 The Approach
To ensure high accuracy while maintaining cost-efficiency, a **Hybrid Multi-Modal Approach** was implemented:

* **Document Tiering:** Recognizing that "Final Orders" are usually digital/selectable while "Lease Deeds" are often scanned images, the pipeline routes documents to different extraction engines. This avoids expensive OCR calls for documents where direct text extraction is possible.
* **Contextual Windowing (Clipped Processing):** Legal Lease Deeds are often 20+ pages long, but key data (Parties, Survey Nos, Dates) usually resides in the preamble or early clauses. The pipeline "clips" these to pages 2–4, significantly reducing token consumption and noise for the LLM.
* **Prompt Engineering via Markdown:** Instead of hardcoded strings, system instructions are maintained in `.md` files. This allows for easier tuning of the extraction logic without touching the Python code.
* **Audit-First Design:** A JSONL-based "Black Box" recorder captures the raw extracted text *before* the LLM sees it. This separates "Extraction Errors" (OCR failures) from "Reasoning Errors" (LLM hallucinations).


## ⚙️ Project Workflow
The pipeline follows a multi-stage orchestration to ensure accuracy and cost-efficiency:

1.  **Pairing & Preprocessing:** * Scans the `inputs/` folder and pairs documents based on the ID found in the filename (e.g., `101_FinalOrder.pdf` and `101_LeaseDeed.pdf`).
    * Clips **Lease Deeds** down to pages **2–4** to focus on relevant clauses and minimize API token usage.
2.  **Hybrid Extraction:**
    * **Final Orders:** Uses `PyMuPDF` (fitz) for fast, direct text extraction from selectable layers.
    * **Lease Deeds:** Uses **Gemini 2.5 Flash** via REST API to perform high-accuracy OCR on scanned pages.
3.  **LLM Reasoning:**
    * Passes extracted text to Gemini using structured **Markdown (.md) prompts** from `prompts_db/`.
    * Consolidates JSON responses from both documents into a single row per Survey ID.
4.  **Consolidation & Audit:**
    * Saves final results to `results.csv`.
    * Maintains a full `audit_log.jsonl` containing the timestamp, doc ID, raw extracted text, and LLM responses for quality debugging.

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repo-link>
cd ComplianceClerk-IntelligentDocumentExtraction
```

### 2. Environment Setup
Create a virtual environment and install the required dependencies:
```bash
python -m venv .venv
# Activate on Windows:
.venv\Scripts\activate
# Activate on macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. API Configuration
Create a `.env` file in the root directory and add your Google Gemini API Key:
```env
GEMINI_API_KEY=your_actual_key_here
```

### 4. Run the Pipeline
Place your PDFs in the `inputs/` folder and execute:
```bash
python main.py
```

## ⚠️ Known Issues & Troubleshooting

### 1. Rate Limiting (Error 429)
If you are using the **Gemini Free Tier**, you may encounter a `429: Too Many Requests` error. 
* **Cause:** The free tier is limited to ~15 Requests Per Minute (RPM).
* **Fix:** The pipeline includes a small delay, but for large batches, it is recommended to process files in groups or upgrade to a "Pay-as-you-go" plan in Google AI Studio.

### 2. Missing Data Points
If a field in the `results.csv` is empty or incorrect:
* Check `audit_log.jsonl`.
* Verify the `extracted_text_source` field in the log. If the text is garbled, the scan quality may be too low for OCR.
* If the source text is clear but the JSON is wrong, refine the prompts in `prompts_db/`.

### 3. Filename Matching
The orchestrator relies on a numeric ID at the start of the filename (e.g., `255_Document.pdf`). Ensure your input files follow this naming convention for proper pairing.

---


