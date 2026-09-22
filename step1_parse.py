"""
STEP 1: PARSE
Raw 10-K HTML -> clean text file per company.
"""
import os
from bs4 import BeautifulSoup

UPLOAD_DIR = "uploads"
OUT_DIR = "parsed"
os.makedirs(OUT_DIR, exist_ok=True)

FILES = {
    "amazon":    "amazon_2025_10k.html",
    "apple":     "apple_2025_10k.html",
    "microsoft": "microsoft_2025_10k.html",
    "nvidia":    "nvidia_2025_10k.html",
    "tesla":     "tesla_2025_10k.html",
}

def clean_html(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, "lxml")

    # kill script/style/junk tags — no need in text
    for tag in soup(["script", "style", "head", "meta", "link"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # collapse blank line spam (SEC html = lots of empty div/table cell)
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)

if __name__ == "__main__":
    for company, fname in FILES.items():
        path = os.path.join(UPLOAD_DIR, fname)
        text = clean_html(path)
        out_path = os.path.join(OUT_DIR, f"{company}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
            print(f"{company:12s} -> {len(text):>10,} chars -> {out_path}")