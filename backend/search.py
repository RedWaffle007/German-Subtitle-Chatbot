# backend/search.py
from pathlib import Path
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
import threading

ROOT = Path(__file__).resolve().parent.parent
EMB_FILE = ROOT / "data" / "subs_embeddings.npz"
META_FILE = ROOT / "data" / "subs_meta.json"

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_session_last_lock = threading.Lock()
_session_last = {}

class SubtitleSearch:
    def __init__(self):
        if not EMB_FILE.exists():
            raise FileNotFoundError("subs_embeddings.npz missing — run embed_subtitles.py")
        if not META_FILE.exists():
            raise FileNotFoundError("subs_meta.json missing — run embed_subtitles.py")

        print("Loading embeddings:", EMB_FILE)
        data = np.load(EMB_FILE)
        self.embeddings = data["embeddings"]

        with open(META_FILE, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        self.nn = NearestNeighbors(n_neighbors=10, metric="euclidean")
        self.nn.fit(self.embeddings)

        self.model = SentenceTransformer(EMBED_MODEL)
        print(f"Index ready ({len(self.meta)} subtitle lines).")

    def query(self, text, session_id=None):
        q = self.model.encode([text], convert_to_numpy=True)
        q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)

        dists, idxs = self.nn.kneighbors(q, n_neighbors=10)
        idxs = idxs[0].tolist()

        # avoid repeating same subtitle in same session
        if session_id is not None:
            with _session_last_lock:
                last = _session_last.get(session_id)

            if last is not None and idxs[0] == last:
                for i in idxs:
                    if i != last:
                        chosen = i
                        break
                else:
                    chosen = idxs[0]
            else:
                chosen = idxs[0]

            with _session_last_lock:
                _session_last[session_id] = chosen
        else:
            chosen = idxs[0]

        return {
            "index": int(chosen),
            "text": self.meta[chosen]["text"],
            "source_file": self.meta[chosen]["source_file"]
        }


_search = None

def get_search():
    global _search
    if _search is None:
        _search = SubtitleSearch()
    return _search
