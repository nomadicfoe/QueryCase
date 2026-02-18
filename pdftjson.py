import os
import json
import fitz  # PyMuPDF
import magic  # for MIME type detection
from bs4 import BeautifulSoup
from tqdm import tqdm

print(fitz.__doc__)

# Directories
PDF_DIR = "./data/pdfs"
JSON_DIR = "./data/json"
os.makedirs(JSON_DIR, exist_ok=True)

# Check MIME type
def get_mime_type(file_path):
    try:
        return magic.from_file(file_path, mime=True)
    except Exception as e:
        print(f"⚠️ MIME check failed for {file_path}: {e}")
        return ""

# Detect error pages
def is_error_text(text):
    error_signatures = [
        "403 Forbidden",
        "404 Not Found",
        "Access Denied",
        "Microsoft-Azure-Application-Gateway",
        "Cloudflare",
        "Nginx",
        "Bad Gateway",
        "Site can’t be reached"
    ]
    return any(sig.lower() in text.lower() for sig in error_signatures)

# Extract from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"❌ Failed to extract PDF: {pdf_path}\n    Reason: {e}")
        return ""

# Extract from HTML
def extract_text_from_html(file_path):
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"❌ Failed to extract HTML: {file_path}\n    Reason: {e}")
        return ""

# Process PDFs and HTMLs
def process_pdfs(pdf_dir, json_dir, min_text_length=50):
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    with tqdm(total=len(pdf_files), desc="Processing files") as pbar:
        for file in pdf_files:
            case_id = os.path.splitext(file)[0]
            pdf_path = os.path.join(pdf_dir, file)
            json_path = os.path.join(json_dir, f"{case_id}.json")

            if os.path.exists(json_path):
                pbar.update(1)
                continue

            mime = get_mime_type(pdf_path)
            if mime == "application/pdf":
                text = extract_text_from_pdf(pdf_path)
                source_type = "pdf"
            elif mime in ["text/html", "application/octet-stream"]:
                text = extract_text_from_html(pdf_path)
                source_type = "html"
            else:
                print(f"🚫 Skipping {file}: unrecognized type ({mime})")
                pbar.update(1)
                continue

            if is_error_text(text) or len(text) < min_text_length:
                print(f"⚠️ Skipping {file}: likely error page or too short")
                pbar.update(1)
                continue

            case_data = {
                "id": case_id,
                "filename": file,
                "source_type": source_type,
                "text": text
            }

            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(case_data, f, indent=2, ensure_ascii=False)
                print(f"✅ Saved: {json_path}")
            except Exception as e:
                print(f"❌ Failed to save JSON for {file}: {e}")

            pbar.update(1)

# Run the converter
process_pdfs(PDF_DIR, JSON_DIR)
