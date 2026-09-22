"""
STEP 3: CHUNK + METADATA TAG
Section txt -> overlapping chunks, each tagged {company, section, chunk_id}
"""
import os, json, glob
from langchain_text_splitters import RecursiveCharacterTextSplitter

IN_DIR = "sections"
OUT_PATH = "chunks.jsonl"

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # ~ token proxy via chars, fine for demo
    chunk_overlap=120,   # keep context continuity across chunk boundary
    separators=["\n\n", "\n", ". ", " ", ""],
)

def run():
    files = sorted(glob.glob(os.path.join(IN_DIR, "*.txt")))
    all_chunks = []

    for path in files:
        fname = os.path.basename(path).replace(".txt", "")
        company, section = fname.split("__")

        with open(path, encoding="utf-8") as f:
            text = f.read()

        pieces = splitter.split_text(text)
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "id": f"{company}__{section}__{i}",
                "company": company,
                "section": section,
                "chunk_index": i,
                "text": piece,
            })

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c) + "\n")

    print(f"total chunks: {len(all_chunks)}")
    by_company = {}
    for c in all_chunks:
        by_company[c["company"]] = by_company.get(c["company"], 0) + 1
    for k, v in sorted(by_company.items()):
        print(f"  {k:12s} {v} chunks")

if __name__ == "__main__":
    run()