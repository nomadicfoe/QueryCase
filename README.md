# QueryCase

**QueryCase** is an intelligent semantic search engine for U.S. court cases. It combines machine learning embeddings with FAISS vector search to help legal professionals and researchers find relevant court opinions based on meaning, not just keywords.

## 🎯 Overview

QueryCase automates the entire workflow from fetching court cases from CourtListener's public API to providing instant semantic search results through a user-friendly Streamlit interface.

## 🏗️ System Architecture

The system follows a data processing pipeline that transforms raw PDFs into a searchable knowledge base:

```
CourtListener API
       ↓
   [Fetch Module]
   - Download PDFs
   - API Integration
       ↓
   [Text Extraction]
   - PyMuPDF Parser
   - JSON Storage
       ↓
   [Summarization]
   - BART Model
   - Concise Summaries
       ↓
   [Embedding Engine]
   - Sentence Transformers
   - 384-D Vectors
   - Text Chunking
       ↓
   [FAISS Indexing]
   - Vector Index
   - Metadata Storage
       ↓
   [Streamlit Web App]
   - Semantic Search
   - Result Display
```

## 📂 Project Structure

```
QueryCase/
├── querycase/
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Streamlit web interface
│   ├── config.py            # Configuration & paths
│   ├── fetch.py             # API integration & PDF download
│   ├── index.py             # FAISS indexing & search
│   ├── embed.py             # Text embedding & vectorization
│   ├── summarizer.py        # Opinion summarization (BART)
│   ├── update.py            # Scheduled index updates
│   └── __pycache__/         # Python cache
├── data/                    # (Ignored in Git)
│   ├── pdfs/                # Downloaded court opinion PDFs
│   ├── json/                # Extracted text as JSON
│   ├── faiss_index.index    # FAISS vector index
│   ├── metadata.json        # Case metadata
│   └── checkpoint.json      # Fetch progress tracking
├── pyproject.toml           # Project dependencies
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── pdftjson.py              # PDF extraction utility
```

## ✨ Features

- **Semantic Search**: Find cases by legal meaning, not just keywords
- **Automated Fetching**: Download and process new cases from CourtListener API
- **PDF Extraction**: Automatically extract text from court opinion PDFs
- **Smart Summarization**: BART-based summaries of long legal opinions
- **Vector Embeddings**: 384-dimensional semantic embeddings
- **Fast Retrieval**: FAISS similarity search for instant results
- **Web Interface**: Beautiful Streamlit UI for easy access
- **Scheduled Updates**: Keep your index fresh with automated updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (for models)
- ~5GB disk space (for models and initial index)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nomadicfoe/QueryCase.git
   cd QueryCase
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   ```

   This installs all dependencies:
   - `requests` - HTTP API calls
   - `pymupdf` - PDF text extraction
   - `sentence-transformers` - Semantic embeddings
   - `faiss-cpu` - Vector similarity search
   - `transformers` & `torch` - BART summarization
   - `streamlit` - Web interface
   - `tqdm` - Progress tracking

### Running the Application

#### 🌐 Option 1: Web Interface (Recommended)
```bash
streamlit run querycase/app.py
```
Opens at `http://localhost:8501`

#### 📥 Option 2: Fetch and Index Cases
```bash
python -m querycase.fetch    # Download cases from CourtListener
python -m querycase.index    # Build FAISS index
```

#### ⏰ Option 3: Update Existing Index
```bash
python -m querycase.update   # Add new cases to index
```

## 🔄 How It Works

### 1. Fetching (`fetch.py`)
The fetcher connects to CourtListener's public API to retrieve cases:
- Searches for cases matching legal terms
- Downloads PDF opinions
- Extracts metadata (judge, date, court)
- Saves as JSON for processing

**Example**: Query "contract breach" → Receives 100+ matching cases

### 2. Summarization (`summarizer.py`)
Long opinions (50+ pages) are summarized using Facebook's BART model:
- Input: Full court opinion text
- Processing: BART neural network
- Output: 80-300 word summary of key rulings
- Purpose: Quick understanding without reading full text

**Benefits**: Faster reading, key points extraction

### 3. Text Embedding (`embed.py`)
Converts text to searchable vectors using sentence transformers:
- Chunks text into 512-token segments
- Converts each chunk to 384-dimensional vector
- Preserves semantic meaning
- Multiple chunks per case for detailed search

**Why**: Enables semantic (meaning-based) search

### 4. Indexing (`index.py`)
Builds searchable index using FAISS:
- Creates vector index from embeddings
- Stores case metadata (name, court, date, summary)
- Enables sub-1ms similarity search
- Updates incrementally with new cases

**Performance**: Search 100k cases in milliseconds

### 5. Searching (`app.py`)
User-friendly Streamlit interface:
- User enters natural language query
- Query converted to vector (same as documents)
- FAISS finds top-k most similar cases
- Results shown with scores and summaries

## 📊 Expected Results

### What You Get
- **Case Title**: Full name of the case
- **Court**: Which court decided (e.g., 9th Circuit, Supreme Court)
- **Decision Date**: When the ruling was made
- **Similarity Score**: How relevant to your query (0.0-1.0, higher = better)
- **Summary**: AI-generated key points from opinion
- **Link**: Direct link to full opinion on CourtListener

### Example Search

**You search**: "What happens when software licenses are violated?"

**QueryCase returns**:
1. *ABC Corp v. XYZ Software* (2022)
   - Court: 11th Circuit
   - Score: 0.92
   - Summary: "Licensee liable for direct damages and lost profits when violating software license terms. Court awarded injunctive relief prohibiting further use..."

2. *Tech Company v. Competitor* (2021)
   - Court: 2nd Circuit
   - Score: 0.87
   - Summary: "License violations trigger both contractual and statutory remedies..."

## ⚙️ Configuration

Edit `querycase/config.py` to customize behavior:

```python
# Paths
JSON_DIR = "data/json"                    # Where extracted cases stored
PDFS_DIR = "data/pdfs"                    # Where PDFs downloaded
INDEX_PATH = "data/faiss_index.index"    # FAISS index location
META_PATH = "data/metadata.json"         # Metadata location

# Processing
MAX_CHUNK_SIZE = 512                      # Tokens per embedding chunk
EMBEDDING_DIM = 384                       # Vector dimensions
TOP_K_RESULTS = 5                         # Results to return per search
```

## 📝 Usage Example

```python
from querycase.index import search_index

# Semantic search
query = "intellectual property infringement"
results = search_index(query, top_k=5)

# Process results
for i, result in enumerate(results, 1):
    print(f"{i}. {result['case_name']}")
    print(f"   Court: {result['court']}")
    print(f"   Score: {result['similarity']:.2%}")
    print(f"   Summary: {result['summary']}\n")
```

## 🔍 Data Flow

```
CourtListener API
       ↓ (PDF files)
   PDF Files
       ↓ extract text (PyMuPDF)
   Extracted Text
       ↓ summarize (BART)
   Text + Summary
       ↓ embed chunks (Sentence-Transformers)
   Vectors + Metadata
       ↓ build index (FAISS)
   ┌─────────────────┐
   │  Searchable     │
   │  Knowledge Base │
   └─────────────────┘
       ↑ (queries)
   User Search
       ↓
   Web Interface
```

## 📋 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web UI** | Streamlit | Interactive search interface |
| **Embeddings** | Sentence-Transformers | Convert text to vectors |
| **Summarization** | BART (facebook/bart-large-cnn) | Summarize opinions |
| **Vector Search** | FAISS | Fast similarity search |
| **PDF Reading** | PyMuPDF | Extract text from PDFs |
| **API** | CourtListener API | Fetch court cases |
| **ML Framework** | PyTorch | Deep learning backend |

## 🔐 Important Notes

### Data Management
- **Local Storage**: `data/` folder is .gitignored to avoid large files on GitHub
- **Each User**: Maintains their own local index
- **Storage**: FAISS index ~100MB per 10k cases

### Resource Requirements
- **Disk**: 5GB for models + index growth
- **RAM**: 4GB minimum (8GB+ recommended)
- **Network**: For initial CourtListener API calls

### First Run
- BART model (~1.6GB) downloads automatically
- Sentence-transformers model (~400MB) downloads automatically
- First indexing may take 30+ minutes depending on case count

### API Usage
- CourtListener has rate limits
- Check their documentation for current limits
- Respects robots.txt and includes delays

## 🛠️ Troubleshooting

### Issue: "Unknown task summarization"
**Fix**: Models need reinstalling
```bash
pip install -e . --force-reinstall
```

### Issue: Streamlit shows errors
**Fix**: Use the correct command
```bash
streamlit run querycase/app.py
```
(Not: `python querycase/app.py`)

### Issue: Out of memory errors
**Fix**: Reduce `MAX_CHUNK_SIZE` in config.py

### Issue: FAISS index not found
**Fix**: Run indexing first
```bash
python -m querycase.fetch
python -m querycase.index
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **CourtListener** - Free public access to court cases
- **Hugging Face** - Sentence-transformers and BART models
- **Meta/Facebook** - FAISS similarity search library
- **OpenAI/Anthropic** - Foundational NLP research

## 📞 Support

- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: README for setup help

---

**Made with ❤️ for the legal tech community**

Last Updated: February 2026
