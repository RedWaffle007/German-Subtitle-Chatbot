import json
from datasets import Dataset


def load_jsonl(path):
    """Load JSONL dataset for training."""
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))
    return Dataset.from_list(data)
