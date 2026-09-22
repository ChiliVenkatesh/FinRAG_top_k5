"""
STEP 6: RETRIEVE
Query -> embed (same vectorizer) -> cosine sim vs stored matrix -> top-k
Filter by company/section metadata BEFORE scoring (fin domain needs this).
"""
import pickle
from sklearn.metrics.pairwise import cosine_similarity

STORE_PATH = "vector_store.pkl"

def load_store():
    with open(STORE_PATH, "rb") as f:
        return pickle.load(f)

def retrieve(query, store, k=4, company=None, section=None):
    vectorizer = store["vectorizer"]
    matrix = store["matrix"]
    metadata = store["metadata"]

    idxs = [
        i for i, m in enumerate(metadata)
        if (company is None or m["company"] == company)
        and (section is None or m["section"] == section)
    ]
    if not idxs:
        return []

    q_vec = vectorizer.transform([query])
    sub_matrix = matrix[idxs]
    sims = cosine_similarity(q_vec, sub_matrix)[0]

    ranked = sorted(zip(idxs, sims), key=lambda x: x[1], reverse=True)[:k]
    results = []
    for idx, score in ranked:
        m = metadata[idx]
        results.append({
            "score": round(float(score), 4),
            "company": m["company"],
            "section": m["section"],
            "text": m["text"][:400],
        })
    return results

if __name__ == "__main__":
    store = load_store()

    print("=== query: research and development expense increase (no filter) ===")
    for r in retrieve("research and development expense increase", store, k=3):
        score = r["score"]
        company = r["company"]
        section = r["section"]
        print("[" + str(score) + "] " + company + " / " + section)
        print("   ", r["text"][:180].replace("\n", " "), "...")

    print()
    print("=== query: supply chain risk filtered company=nvidia section=risk_factors ===")
    for r in retrieve("supply chain risk", store, k=3, company="nvidia", section="risk_factors"):
        score = r["score"]
        company = r["company"]
        section = r["section"]
        print("[" + str(score) + "] " + company + " / " + section)
        print("   ", r["text"][:180].replace("\n", " "), "...")
