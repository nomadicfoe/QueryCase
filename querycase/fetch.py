import os
import json
import requests
import fitz  # PyMuPDF
from datetime import datetime
from tqdm import tqdm
from .config import HEADERS, PDF_DIR, JSON_DIR, LAST_FETCH_PATH

BASE_URL = "https://www.courtlistener.com/api/rest/v4/opinions/"

def get_last_fetch_date():
    if not os.path.exists(LAST_FETCH_PATH):
        return "2022-01-01"
    with open(LAST_FETCH_PATH, "r") as f:
        return f.read().strip()

def update_last_fetch_date(new_date):
    with open(LAST_FETCH_PATH, "w") as f:
        f.write(new_date)

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"❌ Failed to extract text from {pdf_path}: {e}")
        return ""

def fetch_new_cases(max_cases=10):
    print("📡 Connecting to CourtListener...")
    last_date = get_last_fetch_date()
    print(f"📅 Fetching cases since {last_date}")
    params = {
        "date_filed_min": last_date,
        "ordering": "date_filed",
        "court__contains": "ca",  # Change to 'scotus' for Supreme Court
        "page_size": 5
    }

    next_url = BASE_URL
    total_saved = 0
    newest_date = last_date
    valid_cases = []

    with tqdm(total=max_cases, desc="Fetching cases") as pbar:
        while next_url and total_saved < max_cases:
            res = requests.get(next_url, headers=HEADERS, params=params if next_url == BASE_URL else None)
            if res.status_code != 200:
                print("❌ Error:", res.status_code, res.text)
                break

            data = res.json()
            for case in data["results"]:
                case_id = case["id"]
                url = case.get("download_url")
                if not url:
                    continue

                pdf_path = os.path.join(PDF_DIR, f"{case_id}.pdf")
                json_path = os.path.join(JSON_DIR, f"{case_id}.json")

                if os.path.exists(json_path):
                    continue

                try:
                    pdf_response = requests.get(url)
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_response.content)

                    text = extract_text_from_pdf(pdf_path)
                    if len(text) < 200:
                        print(f"⚠️ Skipping short/empty text for case {case_id}")
                        continue

                    case_data = {
                        "id": case_id,
                        "case_name": case.get("case_name"),
                        "date_filed": case.get("date_filed"),
                        "download_url": url,
                        "opinion_text": text
                    }

                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(case_data, f, indent=2)

                    valid_cases.append(case_data)
                    total_saved += 1
                    newest_date = case.get("date_filed", newest_date)
                    pbar.update(1)

                    if total_saved >= max_cases:
                        break

                except Exception as e:
                    print(f"❌ Failed to process case {case_id}: {e}")
                    continue

            next_url = data.get("next")

    update_last_fetch_date(newest_date)
    print(f"✅ Retrieved {len(valid_cases)} valid new cases.")
    return valid_cases
