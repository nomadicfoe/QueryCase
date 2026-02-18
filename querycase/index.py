import faiss
from querycase.summarizer import summarize_texts
from .config import JSON_DIR
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from .config import INDEX_PATH, META_PATH
import re
# match = re.match(...)  # This would overwrite your variable if re was imported

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
    query = input("Enter legal question: ")
    results = search(query)

    for i, result in enumerate(results, 1):
        case_name = result.get("case_name") or "Unnamed Case"
        case_date = result.get("date_filed") or "Unknown Date"
        print(f"\n🔹 Match {i}: {case_name} ({case_date})")
        print(f"Link: {result['link']}")
        print(f"Snippet: {result['snippet'][:500]}...")

    # 🧠 Load full case texts from data/json/<case_id>.json
    full_texts = []
    for result in results[:3]:  # summarize only top 3 results
        case_id = result.get("case_id")
        if not case_id:
            continue
        json_path = os.path.join(JSON_DIR, f"{case_id}.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    case_data = json.load(f)
                    opinion_text = case_data.get("opinion_text", "")
                    if len(opinion_text) >= 300:
                        full_texts.append(opinion_text[:3000])  # trim for summarizer input limit
            except Exception as e:
                print(f"⚠️ Failed to load {case_id}: {e}")

    if full_texts:
        print("\n🧠 Summary of Relevant Cases:\n")
        summary = summarize_texts(query, full_texts)
        print(summary)
    else:
        print("\n⚠️ No usable full texts found for summarization.")



