import os
import re
import json
from langdetect import detect
from tqdm import tqdm

RAW_DIR = "data/raw_subs"
OUT_DIR = "data/cleaned"
OUT_FILE = os.path.join(OUT_DIR, "train.jsonl")


def clean_line(text):
    """Remove timestamps, noise, and keep only clean German subtitle lines."""
    text = text.strip()

    # Remove timestamps
    text = re.sub(r"\d{2}:\d{2}:\d{2}[,\.]\d{3} --> .*", "", text)

    # Remove stage directions: [lacht], (schreit), <i>...</i>
    text = re.sub(r"\[.*?\]|\(.*?\)|<.*?>", "", text)

    # Remove music tags or similar
    text = re.sub(r"\*\*.*?\*\*", "", text)

    text = text.strip()

    # Skip empty or too long/short lines
    if len(text) < 2 or len(text) > 200:
        return None

    # Detect language (skip if not German)
    try:
        if detect(text) != "de":
            return None
    except:
        return None

    return text


def extract_lines_from_srt(filepath):
    """Extract subtitle lines from .srt or text-like files."""
    lines = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = clean_line(line)
            if line:
                lines.append(line)
    return lines


def build_training_examples(lines):
    """
    Format: each example is:
    {
      "instruction": "Reply as the next subtitle line.",
      "input": "<previous line>",
      "output": "<current line>"
    }
    """
    examples = []
    for i in range(1, len(lines)):
        prev_line = lines[i - 1]
        curr_line = lines[i]

        ex = {
            "instruction": "Reply as the next subtitle line in natural German.",
            "input": prev_line,
            "output": curr_line
        }
        examples.append(ex)

    return examples


def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    all_examples = []

    print(f"Processing subtitles from: {RAW_DIR}\n")

    for filename in tqdm(os.listdir(RAW_DIR)):
        if not filename.lower().endswith((".srt", ".vtt", ".txt")):
            continue

        path = os.path.join(RAW_DIR, filename)
        lines = extract_lines_from_srt(path)

        if len(lines) < 5:
            continue  # too little content

        examples = build_training_examples(lines)
        all_examples.extend(examples)

    print(f"\nTotal training examples: {len(all_examples)}")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Saved cleaned dataset → {OUT_FILE}")


if __name__ == "__main__":
    main()
