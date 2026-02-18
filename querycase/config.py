import os

API_KEY = "8c771e44a7c3e3f66ac3000fae301c15d7b007e3"
HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
JSON_DIR = os.path.join(BASE_DIR, "json")
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index.index")
META_PATH = os.path.join(BASE_DIR, "metadata.json")
LAST_FETCH_PATH = os.path.join(BASE_DIR, "checkpoint.json")  # <-- JSON, not TXT!

# Create folders if they don't exist
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
