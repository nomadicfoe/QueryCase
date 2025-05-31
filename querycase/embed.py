import os
import json
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from .config import JSON_DIR, INDEX_PATH, META_PATH, PDF_DIR

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def embed_and_update_index(new_cases):
    # Load or initialize
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        index = faiss.IndexFlatL2(384)  # 384 for MiniLM
        metadata = []

    all_embeddings = []
    new_metadata = []

    for case in tqdm(new_cases, desc="Embedding cases"):
        text = case.get("opinion_text", "")
        if len(text.strip()) < 100:
            continue

        chunks = chunk_text(text)
        for chunk in chunks:
            vec = model.encode(chunk)
            all_embeddings.append(vec)
            new_metadata.append({
                "case_id": case["id"],
                "case_name": case["case_name"],
                "date_filed": case["date_filed"],
                "download_url": case["download_url"],
                "chunk_text": chunk
            })

        # 🧹 Clean up JSON and PDF for this case
        try:
            case_id = str(case["id"])
            json_path = os.path.join(JSON_DIR, f"{case_id}.json")
            pdf_path = os.path.join(PDF_DIR, f"{case_id}.pdf")

            if os.path.exists(json_path):
                os.remove(json_path)
                print(f"🗑️ Deleted {json_path}")

            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ Deleted {pdf_path}")
            else:
                print(f"⚠️ PDF not found: {pdf_path}")

        except Exception as e:
            print(f"⚠️ Could not delete files for case {case.get('id', 'unknown')}: {e}")

    if all_embeddings:
        index.add(np.vstack(all_embeddings))
        metadata.extend(new_metadata)

        # ✅ Save model and metadata
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Embedded and indexed {len(all_embeddings)} chunks.")
    else:
        print("⚠️ No valid chunks to embed.")
