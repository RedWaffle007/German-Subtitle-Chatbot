import streamlit as st
import requests
import uuid
import base64
from pathlib import Path

API_URL = "http://127.0.0.1:5000/chat"


# =========================================================
# BACKGROUND IMAGE (mountains.png in /demo/assets/)
# =========================================================
def set_background(image_path: str, opacity: float = 0.70):
    img_path = Path(image_path)
    if not img_path.exists():
        st.warning(f"Background image not found: {img_path}")
        return

    with open(img_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>

    /* --- BACKGROUND --- */
    .stApp {{
        background: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* --- DARK OVERLAY --- */
    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, {opacity});
        z-index: 0;
    }}

    /* --- ENSURE MAIN CONTENT IS ABOVE OVERLAY --- */
    .main > div[role="main"] {{
        position: relative;
        z-index: 1;
    }}

    /* --- MAKE ALL TEXT WHITE FOR READABILITY --- */
    * {{
        color: #ffffff !important;
    }}

    /* --- CHAT INPUT BAR: USER TYPING TEXT (BLACK) --- */
    .stApp .stChatInputContainer textarea,
    .stApp textarea[data-testid="stChatInput"],
    div[data-testid="stChatInput"] textarea,
    textarea[aria-label="Chat input"] {{
        color: #000000 !important;   /* pure black typing text */
    }}

    .stApp .stChatInputContainer textarea::placeholder,
    textarea[aria-label="Chat input"]::placeholder {{
        color: #cccccc !important;   /* light grey placeholder */
    }}

    /* --- GLASS PANEL FOR CHAT CONTENT --- */
    section.main > div.block-container {{
        background: rgba(0, 0, 0, 0.30);
        padding: 1.5rem;
        border-radius: 12px;
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# APPLY BACKGROUND
set_background("assets/mountains.png", opacity=0.70)


# =========================================================
# PAGE SETUP
# =========================================================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.set_page_config(
    page_title="German Subtitle Chatbot",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 German Subtitle Chatbot")
st.markdown("""
Chat with a bot that responds using lines from **Dark** subtitles.  
You can write in **English or German**.  
It will reply in **German** + an **English translation**.
""")


# =========================================================
# CHAT HISTORY
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])


# =========================================================
# USER INPUT
# =========================================================
user_input = st.chat_input("Type your message in English or German...")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = requests.post(
            API_URL,
            json={
                "session_id": st.session_state.session_id,
                "message": user_input
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            reply_de = data["reply_german"]
            reply_en = data["reply_english"]

            assistant_text = (
                f"**German:** {reply_de}\n\n"
                f"**English:** {reply_en}"
            )

            st.chat_message("assistant").markdown(assistant_text)
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text
            })

        else:
            st.error("Backend error: " + response.text)

    except Exception as e:
        st.error(f"Request failed: {e}")
