"""
STEP 8: GENERATE
Retrieved chunks + query -> LLM prompt -> answer
STEP 9: GUARD
Every $ number in answer must trace back to retrieved chunk text (fin = zero tolerance hallucination)
"""
import re
from step6_7_retrieve import load_store, retrieve

PROMPT_TEMPLATE = """You are a financial analyst assistant. Answer ONLY using the context below.
If the context does not contain the answer, say "not found in provided filings."
Every number you state must appear in the context. Cite company + section for each claim.

CONTEXT:
{context}

QUESTION: {question}

ANSWER (cite company + section for every claim):"""

def build_prompt(question, chunks):
    context = "\n\n".join(
        f"[{c['company'].upper()} / {c['section']}]\n{c['text']}" for c in chunks
    )
    return PROMPT_TEMPLATE.format(context=context, question=question)

def extract_dollar_figures(text):
    # catches $6,411 million / $32.5 billion / $1.2B etc
    return re.findall(r"\$[\d,]+\.?\d*\s*(?:million|billion|B|M)?", text)

def guard_check(answer_text, retrieved_chunks):
    """Every $ figure in answer must appear (as substring) in some retrieved chunk."""
    context_blob = " ".join(c["text"] for c in retrieved_chunks)
    figures = extract_dollar_figures(answer_text)
    flags = []
    for fig in figures:
        num_only = re.sub(r"[^\d.]", "", fig)
        traced = num_only in context_blob.replace(",", "")
        flags.append({"figure": fig, "traced_to_source": traced})
    return flags

if __name__ == "__main__":
    store = load_store()
    question = "What was Tesla's R&D expense in 2025?"
    chunks = retrieve(question, store, k=3, company="tesla", section="mdna")

    prompt = build_prompt(question, chunks)
    print("=== PROMPT SENT TO LLM ===")
    print(prompt[:800], "...\n")

    # --- mock LLM answer (swap with real Claude/GPT API call in prod) ---
    mock_answer = "Tesla's research and development expense was $6,411 million in 2025, per the MD&A section."

    print("=== MOCK ANSWER ===")
    print(mock_answer)

    print("\n=== GUARD CHECK ===")
    for f in guard_check(mock_answer, chunks):
        status = "OK" if f["traced_to_source"] else "FLAG - not in retrieved context"
        print(f"  {f['figure']:15s} -> {status}")