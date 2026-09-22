"""
STEP 2: SECTION SPLIT
Parsed txt -> split into 10-K Items (Business, Risk Factors, MD&A, Financials...)
Heuristic: "Item X" line appears 2x (TOC + real header). Real header = LAST occurrence.
"""
import os, re, json

IN_DIR = "parsed"
OUT_DIR = "sections"
os.makedirs(OUT_DIR, exist_ok=True)

# matches "Item 1A.", "ITEM 7.", "Item 1A.    Risk Factors" etc — case-insensitive
ITEM_RE = re.compile(r"^item\s+(\d{1,2}[a-c]?)\.?\s*(.*)$", re.IGNORECASE)

# sections we actually care about for RAG (skip signature pages, exhibit index etc)
KEEP_ITEMS = {
    "1": "business",
    "1a": "risk_factors",
    "7": "mdna",
    "7a": "market_risk",
    "8": "financial_statements",
}

def find_headers(lines):
    """Return dict: item_number -> LAST line index it appears at."""
    last_seen = {}
    for i, line in enumerate(lines):
        m = ITEM_RE.match(line.strip())
        if m:
            item_num = m.group(1).lower()
            last_seen[item_num] = i   # overwrite -> keeps LAST occurrence
    return last_seen

def split_sections(company):
    with open(os.path.join(IN_DIR, f"{company}.txt"), encoding="utf-8") as f:
        lines = f.read().splitlines()

    headers = find_headers(lines)
    # sort by line position to know where each section ends (= next header start)
    ordered = sorted(headers.items(), key=lambda kv: kv[1])

    sections = {}
    for idx, (item_num, start_line) in enumerate(ordered):
        if item_num not in KEEP_ITEMS:
            continue
        end_line = ordered[idx + 1][1] if idx + 1 < len(ordered) else len(lines)
        body = "\n".join(lines[start_line:end_line]).strip()
        sections[KEEP_ITEMS[item_num]] = body

    return sections

if __name__ == "__main__":
    companies = [f.replace(".txt", "") for f in os.listdir(IN_DIR)]
    manifest = {}
    for company in sorted(companies):
        sections = split_sections(company)
        manifest[company] = {}
        for name, text in sections.items():
            out_path = os.path.join(OUT_DIR, f"{company}__{name}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            manifest[company][name] = len(text)
        print(f"{company:12s} sections found: {list(sections.keys())}")

    with open(os.path.join(OUT_DIR, "_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)