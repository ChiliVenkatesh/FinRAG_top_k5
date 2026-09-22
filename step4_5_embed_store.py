"""
STEP 4: EMBED   (TF-IDF stand-in — swap for OpenAI/sentence-transformers/FinBERT in prod)
STEP 5: STORE   (save matrix + metadata to disk — swap for FAISS/Chroma/Pinecone in prod)
"""
import json, pickle
from sklearn.feature_extraction.text import TfidfVectorizer

CHUNKS_PATH = "chunks.jsonl"
STORE_PATH = "vector_store.pkl"

def run():
    chunks = []
    with open(CHUNKS_PATH, encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))

    texts = [c["text"] for c in chunks]

    # EMBED — fit vectorizer on full corpus, transform every chunk to a vector
    vectorizer = TfidfVectorizer(
        max_features=20000,
        stop_words="english",
        ngram_range=(1, 2),   # unigram + bigram — catch fin phrases like "operating margin"
    )
    matrix = vectorizer.fit_transform(texts)   # shape: (n_chunks, n_features)

    # STORE — everything needed for retrieval, saved together
    store = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "metadata": [
            {"id": c["id"], "company": c["company"], "section": c["section"], "text": c["text"]}
            for c in chunks
        ],
    }
    with open(STORE_PATH, "wb") as f:
        pickle.dump(store, f)

    print(f"stored {matrix.shape[0]} chunks x {matrix.shape[1]} features -> {STORE_PATH}")

if __name__ == "__main__":
    run()