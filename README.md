# 📊 FinRAG — 10-K Financial Filing Search

A retrieval-augmented generation (RAG) pipeline for searching and answering questions over 2025 10-K filings from five companies: **Amazon, Apple, Microsoft, Nvidia, and Tesla**. Built with a from-scratch TF-IDF retrieval store and a numeric hallucination guard, served through a Streamlit search UI.

## Pipeline

The project is a 9-step pipeline, one script per stage:

| Step | Script | Job |
|---|---|---|
| 1. Parse | `step1_parse.py` | Raw 10-K HTML → clean per-company text |
| 2. Section split | `step2_split.py` | Splits each filing into 10-K Items (Business, Risk Factors, MD&A, Market Risk, Financial Statements) |
| 3. Chunk | `step3_chunk.py` | Splits sections into overlapping chunks, tagged with `{company, section, chunk_id}` |
| 4. Embed | `step4_5_embed_store.py` | TF-IDF vectorization of all chunks (swap-in point for OpenAI/sentence-transformers/FinBERT) |
| 5. Store | `step4_5_embed_store.py` | Saves the vectorizer + matrix + metadata to `vector_store.pkl` (swap-in point for FAISS/Chroma/Pinecone) |
| 6. Retrieve | `step6_7_retrieve.py` | Cosine-similarity top-k search, filterable by company/section |
| 7. Filter | `step6_7_retrieve.py` | Company/section metadata filtering applied before scoring |
| 8. Generate | `step8_9_generate_guard.py` | Builds a context-grounded prompt and generates an answer |
| 9. Guard | `step8_9_generate_guard.py` | Checks every `$` figure in the answer traces back to a retrieved chunk — flags anything not sourced from the filings |

## Features

- 🔍 Semantic search across all five companies' filings
- 🏷️ Filter by company and/or 10-K section
- 🛡️ Hallucination guard — every dollar figure in a generated answer is checked against retrieved source text
- ⚡ Lightweight TF-IDF store — runs with no external vector DB or paid embedding API

## Tech Stack

- **UI:** Streamlit
- **Parsing:** BeautifulSoup4 (`lxml`)
- **Chunking:** LangChain (`RecursiveCharacterTextSplitter`)
- **Vectorization / retrieval:** scikit-learn (`TfidfVectorizer`, cosine similarity)
- **Storage:** pickle

## Project Structure

```
.
├── app.py                        # Streamlit search UI
├── step1_parse.py                 # HTML -> clean text
├── step2_split.py                 # Text -> 10-K item sections
├── step3_chunk.py                 # Sections -> overlapping chunks (chunks.jsonl)
├── step4_5_embed_store.py         # Chunks -> TF-IDF vector store (vector_store.pkl)
├── step6_7_retrieve.py            # Query -> top-k retrieval
├── step8_9_generate_guard.py      # Retrieval -> grounded answer + numeric guard check
├── uploads/                       # Raw 10-K HTML filings (not included — see Data below)
├── parsed/                        # Output of step 1 (generated)
├── sections/                      # Output of step 2 (generated)
├── chunks.jsonl                   # Output of step 3 (generated)
└── vector_store.pkl               # Output of steps 4-5 (generated)
```

> **Repo cleanup needed before pushing:** `step6_7_retrieve - Copy.py` is a duplicate of `step6_7_retrieve.py` — remove it. Also consider **not** committing `chunks.jsonl`, `vector_store.pkl`, or the raw/parsed 10-K text — these are large, regeneratable artifacts and the raw filings may carry redistribution restrictions; a `.gitignore` covering `uploads/`, `parsed/`, `sections/`, `chunks.jsonl`, and `vector_store.pkl` is worth adding.

## Data

Place the raw 10-K HTML filings in an `uploads/` folder before running the pipeline:

```
uploads/
├── amazon_2025_10k.html
├── apple_2025_10k.html
├── microsoft_2025_10k.html
├── nvidia_2025_10k.html
└── tesla_2025_10k.html
```

Filings can be downloaded directly from the SEC's EDGAR database.

## Setup

1. **Clone the repo**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit beautifulsoup4 lxml langchain-text-splitters scikit-learn
   ```

3. **Run the pipeline** (in order, from the project root)
   ```bash
   python step1_parse.py
   python step2_split.py
   python step3_chunk.py
   python step4_5_embed_store.py
   ```

4. **Launch the search app**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Type a question about the filings (e.g. *"research and development expense increase"*).
2. Optionally filter by company and/or section.
3. Click **Search** to see the top matching chunks, ranked by similarity score.

To try the generation + guard step directly:
```bash
python step8_9_generate_guard.py
```

## Notes

- The generation step currently uses a mock LLM answer as a placeholder — swap in a real Claude/GPT API call for production use.
- Zero tolerance for hallucinated numbers: the guard step flags any `$` figure in a generated answer that can't be traced back to retrieved source text.

## License

MIT (or update as needed).
