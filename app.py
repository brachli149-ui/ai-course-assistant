import os
import json
import pathlib
import streamlit as st
from dotenv import load_dotenv
from course_knowledge import get_system_prompt

# ───────────────────────────────
# Setup
# ───────────────────────────────
load_dotenv()
st.set_page_config(
    page_title="AI Kurs-Assistent | Röne Gasser",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────────────
# CSS Styling
# ───────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    :root {
      --bg: #B2D4B2;
      --card: #FFFFFF;
      --border: #D7E6D7;
      --badge-bg: #EDF4FF;
      --badge-text: #2F46C6;
    }

    /* Hintergrund inkl. Header */
    .stApp { background: var(--bg) !important; }
    header[data-testid="stHeader"] {
      background: var(--bg) !important;
      border-bottom: none !important;
      height: 3.5rem !important;
    }

    /* Content-Container */
    .block-container {
      max-width: 980px !important;
      padding-top: 2.2rem !important;
      padding-bottom: 4rem !important;
    }

    /* Titelbereich */
    .header-wrap {
      display: flex;
      align-items: center;
      gap: 0.8rem;
      margin-bottom: 0.4rem;
    }
    .header-wrap img {
      height: 48px;
      width: auto;
      border-radius: 6px;
    }
    .header-title {
      font-size: 2.1rem;
      font-weight: 800;
      margin: 0;
      line-height: 1.2;
      color: #0B1220;
    }
    .header-subtitle {
      margin: 0.3rem 0 1.0rem 3.4rem;
      font-style: italic;
      color: #273a2f;
    }
    .badge {
      display: inline-block;
      padding: 3px 8px;
      margin-left: 8px;
      background: var(--badge-bg);
      color: var(--badge-text);
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      vertical-align: middle;
    }

    /* Chatbereich */
    [data-testid="stChatMessage"] {
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--card);
      padding: 10px 12px;
      margin: 8px 0;
      box-shadow: 0 1px 2px rgba(10,14,29,0.06);
    }
    [data-testid="stChatInput"] textarea {
      border-radius: 12px !important;
      border: 1px solid var(--border) !important;
      background: #fff !important;
      font-size: 15px;
    }
    [data-testid="stChatInput"] button {
      border-radius: 12px !important;
      font-weight: 700;
      padding: .5rem .9rem !important;
    }

    /* Buttons */
    .stButton>button {
      border-radius: 12px !important;
      font-weight: 700 !important;
      border: 1px solid #0001 !important;
      box-shadow: 0 1px 2px rgba(10,14,29,0.06) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
      background: #fff;
      border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] h2 {
      margin-top:.2rem; margin-bottom:.4rem;
    }

    /* Drei Buttons nebeneinander */
    .row-1line { display:flex; gap:.5rem; align-items:center; }

    /* Logo unten rechts */
    .bottom-logo {
      position: fixed;
      right: 25px;
      bottom: 20px;
      opacity: 0.5;
      z-index: 100;
    }
    .bottom-logo img {
      height: 60px;
      border-radius: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ───────────────────────────────
# Header mit Logo + Titel
# ───────────────────────────────
logo_path = pathlib.Path("logo.jpg")
st.markdown("<div class='header-wrap'>", unsafe_allow_html=True)

if logo_path.exists():
    st.markdown(f"<img src='file://{logo_path.resolve()}' alt='Logo' />", unsafe_allow_html=True)
else:
    st.markdown("<div style='width:48px;height:48px;'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div>
        <h1 class="header-title">AI Kurs-Assistent | Röne Gasser <span class="badge">Beta</span></h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<p class='header-subtitle'>Ihr persönlicher Assistent für den AI Development Kurs</p>", unsafe_allow_html=True)

# ───────────────────────────────
# AI Client Setup
# ───────────────────────────────
def init_ai_client():
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    try:
        if not openai_key:
            openai_key = st.secrets.get("OPENAI_API_KEY", None)
        if not anthropic_key:
            anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    except Exception:
        pass

    if openai_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=openai_key), "openai"
        except Exception:
            st.error("OpenAI-Client konnte nicht geladen werden.")
            return None, None

    if anthropic_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=anthropic_key), "anthropic"
        except Exception:
            st.error("Anthropic-Client konnte nicht geladen werden.")
            return None, None

    st.error("⚠️ Kein API-Key gefunden (OPENAI_API_KEY oder ANTHROPIC_API_KEY).")
    return None, None

# ───────────────────────────────
# Antwortlogik
# ───────────────────────────────
def get_ai_response(client, client_type, messages):
    try:
        if client_type == "openai":
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            return resp.choices[0].message.content

        elif client_type == "anthropic":
            system_msg = ""
            non_sys = []
            for m in messages:
                if m["role"] == "system":
                    system_msg = m["content"]
                else:
                    non_sys.append({"role": m["role"], "content": m["content"]})
            resp = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.7,
                system=system_msg,
                messages=non_sys,
            )
            return getattr(resp.content[0], "text", str(resp))
    except Exception as e:
        return f"Fehler bei der AI-Anfrage: {e}"

# ───────────────────────────────
# Sidebar mit Infos & Chatverlauf
# ───────────────────────────────
with st.sidebar:
    st.header("ℹ️ Über den Assistenten")
    st.markdown("""
    Dieser Assistent hilft bei:
    - **Kursinhalten** und Konzepten  
    - **Übungen** und Aufgaben  
    - **Tools** und Technologien  
    - **Troubleshooting** bei Problemen  
    """)

    st.divider()
    st.subheader("🗓️ Kursübersicht")
    st.markdown("""
    **Abend 1:** Grundlagen & No-Code  
    **Abend 2:** Python & Deployment  
    **Abend 3:** LangChain & RAG  
    **Abend 4:** Fortgeschrittene Konzepte  
    **Abend 5:** Eigene Projekte  
    **Abend 6:** Präsentationen  
    """)

    st.divider()
    st.subheader("🍀 Chat-Verlauf")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Speichern", use_container_width=True):
            st.download_button(
                "Download JSON",
                data=json.dumps(st.session_state.get("messages", []), ensure_ascii=False, indent=2),
                file_name="chatverlauf.json",
                mime="application/json",
                use_container_width=True,
            )
    with col2:
        upload = st.file_uploader("Laden", type=["json"], label_visibility="collapsed")
        if upload:
            st.session_state.messages = json.loads(upload.read().decode("utf-8"))
            st.success("Chat geladen.")
            st.rerun()
    with col3:
        if st.button("🗑️ Löschen", use_container_width=True):
            st.session_state.messages = []
            st.success("Chat gelöscht.")
            st.rerun()

# ───────────────────────────────
# Hauptbereich
# ───────────────────────────────
st.header("💬 Stellen Sie Ihre Frage")

client, ctype = init_ai_client()
if not client:
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

frage = st.chat_input("Ihre Frage zum AI Development Kurs...")
if frage:
    st.session_state.messages.append({"role": "user", "content": frage})
    with st.chat_message("user"):
        st.markdown(frage)
    with st.chat_message("assistant"):
        with st.spinner("Denke nach..."):
            full_msgs = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages
            antwort = get_ai_response(client, ctype, full_msgs)
            st.markdown(antwort)
    st.session_state.messages.append({"role": "assistant", "content": antwort})

st.button("♻️ Chat zurücksetzen", on_click=lambda: (st.session_state.update(messages=[]), st.rerun()))

# ───────────────────────────────
# Logo unten rechts fix einblenden
# ───────────────────────────────
if logo_path.exists():
    st.markdown(
        f"""
        <div class="bottom-logo">
            <img src="file://{logo_path.resolve()}" alt="Logo unten rechts" />
        </div>
        """,
        unsafe_allow_html=True,
    )