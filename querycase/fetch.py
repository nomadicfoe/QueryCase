import os
import json
import requests
import fitz  # PyMuPDF
from tqdm import tqdm
from .config import HEADERS, PDF_DIR, JSON_DIR, LAST_FETCH_PATH
from datetime import datetime
import time

BASE_URL = "https://www.courtlistener.com/api/rest/v4/opinions/"

# Load checkpoint (date_filed + last_case_id)
def get_checkpoint():
    try:
        with open(LAST_FETCH_PATH, "r") as f:
            content = f.read()
            print("📄 RAW checkpoint content from disk:")
            print(repr(content))  # see all hidden characters
            return json.loads(content)
    except Exception as e:
        print(f"❌ JSON read error: {e}")
        return {"date_filed": "2015-01-01", "last_case_id": 0}


# Save checkpoint after each successful case
def update_checkpoint(date_filed, case_id):
    with open(LAST_FETCH_PATH, "w") as f:
        json.dump({"date_filed": date_filed, "last_case_id": case_id}, f)

# Extract text from a single PDF
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

# Fetch new cases in batches, resuming from last checkpoint
def fetch_new_case_batches(batch_size=50, court_filter="ca"):
    checkpoint = get_checkpoint()
    min_date = checkpoint["date_filed"]
    min_case_id = checkpoint["last_case_id"]

    print(f"📡 Connecting to CourtListener (since {min_date} / ID > {min_case_id})")

    params = {
        "date_filed_min": min_date,
        "ordering": "date_filed",
        "court__contains": court_filter,
        "page_size": 100
    }

    next_url = BASE_URL
    total_fetched = 0
    batch = []

    with tqdm(desc="Fetching cases") as pbar:
        while next_url:
            try:
                res = requests.get(next_url, headers=HEADERS, params=params if next_url == BASE_URL else None, timeout=30)
                if res.status_code != 200:
                    print(f"❌ API error {res.status_code}: {res.text}")
                    break

                data = res.json()
                for case in data["results"]:
                    case_id = case["id"]
                    case_date = case.get("date_filed")
                    url = case.get("download_url")

                    if not url or not case_date:
                        continue

                    # Skip already processed cases
                    if case_date < min_date:
                        continue
                    if case_date == min_date and case_id <= min_case_id:
                        continue

                    pdf_path = os.path.join(PDF_DIR, f"{case_id}.pdf")
                    json_path = os.path.join(JSON_DIR, f"{case_id}.json")

                    if os.path.exists(json_path):
                        continue

                    try:
                        response = requests.get(url, timeout=30)
                        with open(pdf_path, "wb") as f:
                            f.write(response.content)

                        text = extract_text_from_pdf(pdf_path)

                        # Always delete the PDF (regardless of outcome)
                        if os.path.exists(pdf_path):
                            try:
                                os.remove(pdf_path)
                                print(f"🗑️ Deleted PDF for case {case_id}")
                            except Exception as e:
                                print(f"⚠️ Could not delete PDF for case {case_id}: {e}")

                        if len(text) < 200:
                            print(f"⚠️ Skipping case {case_id}: text too short")
                            continue

                        case_data = {
                            "id": case_id,
                            "case_name": case.get("case_name"),
                            "date_filed": case_date,
                            "download_url": url,
                            "opinion_text": text
                        }

                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(case_data, f, indent=2)

                        batch.append(case_data)
                        total_fetched += 1
                        pbar.update(1)

                        # ✅ Update checkpoint
                        update_checkpoint(case_date, case_id)

                        if len(batch) >= batch_size:
                            yield batch
                            batch = []

                        time.sleep(0.5)  # polite delay

                    except Exception as e:
                        print(f"❌ Error processing case {case_id}: {e}")
                        continue

                next_url = data.get("next")
            except Exception as e:
                print(f"❌ Network error: {e}")
                time.sleep(10)  # wait and retry

    if batch:
        yield batch

    print(f"✅ Done. Total valid cases fetched: {total_fetched}")
