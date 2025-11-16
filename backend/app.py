# backend/app.py

from flask import Flask, request, jsonify
from search import get_search
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)

# load search engine (embeddings)
searcher = get_search()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

def translate_to_german(text):
    """Translate any language (mainly English) to German."""
    try:
        return GoogleTranslator(source='auto', target='de').translate(text)
    except:
        return text  # fallback: return original

def translate_to_english(text):
    """Translate German subtitle line to English."""
    try:
        return GoogleTranslator(source='de', target='en').translate(text)
    except:
        return text  # fallback

@app.route("/chat", methods=["POST"])
def chat():
    """
    POST /chat
    {
        "session_id": "abc",
        "message": "hello"
    }

    Returns:
    {
        "reply_german": "...",
        "reply_english": "...",
        "source_file": "Dark.S01E01.srt",
        "input_used_for_search": "Hallo"
    }
    """
    data = request.get_json(force=True)

    if not data or "message" not in data:
        return jsonify({"error": "'message' is required"}), 400

    user_msg = data["message"]
    session_id = data.get("session_id")

    # Convert English → German (or keep German as-is)
    german_input = translate_to_german(user_msg)

    # Retrieve best-matching subtitle (German)
    retrieved = searcher.query(german_input, session_id=session_id)
    german_reply = retrieved["text"]

    # Translate German subtitle → English
    english_reply = translate_to_english(german_reply)

    return jsonify({
        "reply_german": german_reply,
        "reply_english": english_reply,
        "source_file": retrieved["source_file"],
        "input_used_for_search": german_input
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
