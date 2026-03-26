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

    def call_llm(self, prompt, context_text, doc_id, doc_type):
        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nDocument Content:\n{context_text}"}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.1}
        }
        
        response = requests.post(self.url, json=payload)
        res_data = response.json()
        
        # Extract response text
        try:
            raw_response = res_data['candidates'][0]['content']['parts'][0]['text']
            parsed_json = json.loads(raw_response)
        except Exception as e:
            raw_response = str(res_data)
            parsed_json = {"error": "Failed to parse JSON", "raw": raw_response}

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "doc_id": doc_id,
            "doc_type": doc_type,
            "extracted_text_source": context_text,  # <--- Added this
            "input_prompt": prompt,
            "raw_llm_response": raw_response
        }
        with open(self.audit_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return parsed_json