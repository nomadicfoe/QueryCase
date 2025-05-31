import faiss
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from .config import INDEX_PATH, META_PATH

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=5):
    """
    Semantic search for the most relevant case snippets.
    """
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        print("❌ FAISS index or metadata not found.")
        return []

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), top_k)

    results = []
    for idx in indices[0]:
        match = metadata[idx]
        results.append({
            "case_name": match["case_name"],
            "date_filed": match["date_filed"],
            "snippet": match["chunk_text"][:500],
            "link": match["download_url"]
        })
    return results

# Example interactive usage:
if __name__ == "__main__":
    q = input("Enter legal question: ")
    matches = search(q)
    for i, m in enumerate(matches, 1):
        print(f"\n🔹 Match {i}: {m['case_name']} ({m['date_filed']})")
        print(f"Link: {m['link']}")
        print(f"Snippet: {m['snippet']}")
