import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-2.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        self.audit_log = "audit_log.jsonl"

    def call_llm(self, prompt, context_text):
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nDocument Content:\n{context_text}"}]}],
            "generationConfig": {
                "response_mime_type": "application/json", 
                "temperature": 0.1
            }
        }
        
        response = requests.post(self.url, json=payload)
        res_data = response.json()
        
        try:
            # 1. Extract the text response
            raw_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

            # --- VISUAL PRINT SECTION ---
            print("\n" + "="*60)
            print("🚀 RAW LLM RESPONSE:")
            print("-" * 60)
            print(raw_response)
            print("="*60 + "\n")
            # ----------------------------

            # 2. Clean up markdown if LLM accidentally included it
            if raw_response.startswith("```"):
                raw_response = raw_response.strip("```json").strip("```").strip()

            parsed_json = json.loads(raw_response)
            
        except Exception as e:
            print(f"❌ ERROR PROCESSING RESPONSE: {e}")
            raw_response = str(res_data)
            parsed_json = {"error": "Failed to parse JSON", "raw": raw_response}

        # 3. Logging for Audit
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": raw_response
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return parsed_json