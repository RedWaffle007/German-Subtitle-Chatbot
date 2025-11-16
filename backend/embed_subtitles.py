# backend/embed_subtitles.py
"""
Extract lines from raw_subs/*.srt, filter short lines,
embed with sentence-transformers, and save metadata + embeddings.
"""

import re
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW_SUBS = ROOT / "data" / "raw_subs"
OUT_EMB = ROOT / "data" / "subs_embeddings.npz"
OUT_META = ROOT / "data" / "subs_meta.json"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def parse_srt(path):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    blocks = re.split(r"\n{2,}", text.strip())
    lines = []
    for b in blocks:
        b_lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
        if not b_lines:
            continue

        clean_lines = []
        for ln in b_lines:
            if re.match(r"^\d+$", ln):
                continue
            if re.search(r"\d{2}:\d{2}:\d{2},\d{3}", ln):
                continue
            clean_lines.append(ln)

        if clean_lines:
            lines.append(" ".join(clean_lines))

    return lines

def clean_line(s):
    s = s.strip()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return s

def main():
    print("Loading embedding model:", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    all_lines = []
    metas = []
    seen = set()

    print("Reading:", RAW_SUBS)

    for p in sorted(RAW_SUBS.glob("*.srt")):
        parsed = parse_srt(p)
        for ln in parsed:
            ln = clean_line(ln)
            if not ln:
                continue

            if len(ln) < 20:      # important filter!
                continue

            if ln.lower() in {"ja", "nein", "okay", "ok", "huh", "hm", "hmm"}:
                continue

            if ln in seen:
                continue
            seen.add(ln)

            metas.append({"text": ln, "source_file": p.name})
            all_lines.append(ln)

    print(f"Kept {len(all_lines)} subtitle lines.")

    embeddings = model.encode(all_lines, show_progress_bar=True, convert_to_numpy=True)

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    embeddings = embeddings / norms

    np.savez_compressed(OUT_EMB, embeddings=embeddings)
    with open(OUT_META, "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    print("Saved:")
    print(" -", OUT_EMB)
    print(" -", OUT_META)

if __name__ == "__main__":
    main()
