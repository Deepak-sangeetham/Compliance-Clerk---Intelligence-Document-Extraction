import os
import base64
import requests
from dotenv import load_dotenv
from pathlib import Path

# 1. Setup Environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

# 2. Configuration
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def extract_pdf_with_rest(pdf_path):
    # Read and encode the PDF to Base64
    path = Path(pdf_path)
    if not path.exists():
        return f"Error: File {pdf_path} not found."
    
    with open(path, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    # 3. Construct the Payload
    # Gemini REST uses 'inlineData' for base64 files
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "OCR this document. Extract all text and tables accurately."},
                    {
                        "inlineData": {
                            "mimeType": "application/pdf",
                            "data": pdf_base64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,      # Lower for better OCR accuracy
            "maxOutputTokens": 21920, # Ensure enough room for full document text
            "thinking_config": {
                "include_thoughts": False # Set to True if you want to see reasoning
            }
        }
    }

    headers = {"Content-Type": "application/json"}

    # 4. Make the Request
    response = requests.post(URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Navigate the response JSON to get the text
        return data['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"Error {response.status_code}: {response.text}"

