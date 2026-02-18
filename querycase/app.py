import os
import json
import faiss
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer

# Adjust these imports based on how your package is structured
# If this file lives inside the `querycase` package, keep as-is;
# if it's outside, change to: from querycase.config import ...
from querycase.summarizer import summarize_texts
from querycase.config import JSON_DIR, INDEX_PATH, META_PATH

# -----------------------------
# CACHED HELPERS
# -----------------------------

@st.cache_resource
def load_model():
    """
    Load the SentenceTransformer model once, and reuse it across reruns.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_resource
def load_index_and_metadata():
    """
    Load the FAISS index and metadata JSON only once.
    Returns (index, metadata) or (None, None) if unavailable.
    """
    if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
        return None, None

    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return index, metadata


# -----------------------------
# CORE SEARCH FUNCTION
# -----------------------------

def search_cases(query: str, top_k: int = 5):
    """
    Semantic search for the most relevant case snippets.
    Returns a list of dicts with case info.
    """
    index, metadata = load_index_and_metadata()
    if index is None or metadata is None:
        return []

    model = load_model()
    # Encode query into embedding
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding, dtype=np.float32), top_k)

    results = []
    for idx in indices[0]:
        # Safety: ensure idx is within metadata bounds
        if idx < 0 or idx >= len(metadata):
            continue
        match = metadata[idx]

        # Include case_id if available in your metadata
        case_id = match.get("case_id")

        results.append({
            "case_id": case_id,
            "case_name": match.get("case_name") or "Unnamed Case",
            "date_filed": match.get("date_filed") or "Unknown Date",
            "snippet": (match.get("chunk_text") or "")[:500],
            "link": match.get("download_url") or "",
        })
    return results


def load_full_texts_for_summary(results, max_cases: int = 3, max_chars: int = 3000):
    """
    Load full case texts from the JSON_DIR for the top results to feed into the summarizer.
    We:
    - Look at at most `max_cases` cases
    - Trim each case to `max_chars` characters to keep summarization manageable
    """
    full_texts = []

    for result in results[:max_cases]:
        case_id = result.get("case_id")
        if not case_id:
            continue

        json_path = os.path.join(JSON_DIR, f"{case_id}.json")
        if not os.path.exists(json_path):
            continue

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                case_data = json.load(f)
                opinion_text = case_data.get("opinion_text", "")
                # Only use reasonably long texts
                if len(opinion_text) >= 300:
                    full_texts.append(opinion_text[:max_chars])
        except Exception as e:
            # Show a small warning in the UI but continue
            st.warning(f"Failed to load case {case_id}: {e}")

    return full_texts


# -----------------------------
# STREAMLIT UI
# -----------------------------

def main():
    st.set_page_config(
        page_title="QueryCase – Case Law Semantic Search",
        page_icon="⚖️",
        layout="wide",
    )

    st.title("⚖️ QueryCase – Case Law Semantic Search")
    st.markdown(
        "Ask a legal question or describe an issue, and I'll show the most relevant cases from your FAISS index."
    )

    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Number of results (top_k)", min_value=1, max_value=20, value=5)
        summarize_toggle = st.checkbox("Summarize top cases", value=True)
        max_cases_for_summary = st.slider(
            "Max cases to summarize", min_value=1, max_value=5, value=3
        )

    # Check that index & metadata exist
    index, metadata = load_index_and_metadata()
    if index is None or metadata is None:
        st.error(
            "❌ FAISS index or metadata not found.\n\n"
            f"Expected:\n- INDEX_PATH: `{INDEX_PATH}`\n- META_PATH: `{META_PATH}`"
        )
        st.stop()

    # Query input
    query = st.text_area(
        "Enter your legal question or search query:",
        placeholder="e.g., 'What are the key precedents on qualified immunity in police misconduct cases?'",
        height=100,
    )

    search_button = st.button("🔍 Search Cases")

    if search_button and query.strip():
        with st.spinner("Searching relevant cases..."):
            results = search_cases(query, top_k=top_k)

        if not results:
            st.warning("No results found for this query.")
            return

        st.subheader("🔎 Search Results")
        for i, result in enumerate(results, start=1):
            case_name = result["case_name"]
            case_date = result["date_filed"]
            link = result["link"]
            snippet = result["snippet"]

            with st.expander(f"Match {i}: {case_name} ({case_date})"):
                if link:
                    st.markdown(f"[Open case PDF]({link})")
                st.markdown("**Snippet:**")
                st.write(snippet + "…")

        # Summarization
        if summarize_toggle:
            st.subheader("🧠 Summary of Relevant Cases")
            if st.button("Generate summary from top cases"):
                with st.spinner("Summarizing top cases..."):
                    full_texts = load_full_texts_for_summary(
                        results, max_cases=max_cases_for_summary
                    )

                    if full_texts:
                        summary = summarize_texts(query, full_texts)
                        st.markdown("#### Summary")
                        st.write(summary)
                    else:
                        st.warning(
                            "No usable full texts found for summarization. "
                            "Make sure JSON case files exist in JSON_DIR."
                        )
    elif search_button:
        st.warning("Please enter a query before searching.")


if __name__ == "__main__":
    main()
