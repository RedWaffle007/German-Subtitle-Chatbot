# 🎬 German Subtitle Chatbot  
*A lightweight Streamlit app that answers using subtitle lines from the hit German series **Dark**, with automatic English translation.*

This project was built as a practical, interactive demonstration of a retrieval-based chatbot.  
Instead of generating new text from a large model, it finds and returns the closest matching subtitle lines and translates them for bilingual clarity.  
It’s simple, fast, and surprisingly fun to chat with.

---

## Motivation
Learning foreign languages has always been my hobby and the best way to learn is by imitating real conversations. However, having a chat partner to practise 24*7 is invaluable.
Hence, I decided to create this engaging chatbot that uses subtitles from TV shows as responses.
Subtitles from TV shows capture natural phrases, everyday expressions, and a wide vocabulary. This helps me improve my German and builds confidence.
It’s also ideal for beginners and intermediate learners who want exposure to the 20% of German that appears most often in conversations.

---

## Live Demo (Hugging Face)
You can try the chatbot here:  

 **https://huggingface.co/spaces/RedWaffle/German-Subtitle-Chatbot**

Runs fully on CPU using the lightweight retrieval system

---

## Features:

### Retrieval-based “speaking in subtitles”
The chatbot searches your input through thousands of subtitle lines and picks the one closest in meaning using semantic embeddings.

### English ↔ German support
You can type in English or German and the app handles:
1. Translation to German  
2. Subtitle retrieval  
3. Translation back to English  

### Clean Streamlit interface
- Background image with a subtle overlay
- Chat history  
- Automatic input clearing  
- No duplicate messages  
- Smooth UX even on limited hardware  

### Technically solid but lightweight
Uses:
- `sentence-transformers/all-MiniLM-L6-v2`
- Precomputed embeddings (`subs_embeddings.npz`)
- Cosine similarity for matching
- `deep-translator` for translation

### Extra work: A fine-tuned model (not shipped)
A LoRA-fine-tuned Mistral model was also trained for ~9 hours during experimentation.  
It is **not included in this repository** to keep the repo lean,  
but the work is documented as part of the project’s exploration.

---

## Project Structure

```

backend/
data/
demo/
docs/

````

---

## Running Locally

### 1. Install dependencies  
```bash
pip install -r requirements.txt
````

### 2. Launch Streamlit

```bash
streamlit run demo/streamlit_app.py
```

---

## How It Works

1. **Subtitle extraction**
   Subtitle `.srt` files are cleaned, deduplicated, and stored with metadata.

2. **Embedding generation**
   Each line is encoded once using MiniLM and saved to disk.

3. **Semantic search**
   User query → translated → embedded → cosine matching → top line returned.

4. **Translation & formatting**
   Output includes:

   * the original German subtitle
   * an English translation labeled clearly as **Translation:**

---



