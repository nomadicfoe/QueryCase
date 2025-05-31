# QueryCase

**QueryCase** is a Python package that lets you fetch, parse, and semantically search U.S. court cases using CourtListener’s public API and PDF-based opinion extraction.

## Features
- 🔍 Retrieve court cases based on a legal query
- 📥 Automatically download and extract new opinions from CourtListener
- 🧠 Chunk and embed opinions using sentence transformers
- 📦 Store and retrieve using FAISS vector search
- 🔁 Supports scheduled updates to stay current

## Install
```bash
pip install -e .
