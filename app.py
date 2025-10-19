import os
import json
import datetime as dt

import streamlit as st
from dotenv import load_dotenv
from course_knowledge import get_system_prompt

# --------------------------------------------------------------
# 1️⃣ .env laden (falls vorhanden)
# --------------------------------------------------------------
load_dotenv()

# --------------------------------------------------------------
# 2️⃣ Streamlit-Seite konfigurieren
# --------------------------------------------------------------
st.set_page_config(
    page_title="AI Kurs-Assistent | Röne Gasser",
    page_icon="ᾑ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------
# 3️⃣ CSS Styling
# --------------------------------------------------------------
def inject_css():
    st.markdown(
        """
<style>
.stApp { background: linear-gradient(180deg,#F7F8FB 0%,#F2F4F8 100%); }
.block-container { max-width: 980px !important; padding-top: 2rem !important; padding-bottom: 5rem !important; }
section[data-testid="stSidebar"] { width: 320px !important; background:#FFF; border-right:1px solid #E6E8EF; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { font-weight:700; }
h1 { letter-spacing:.3px; }
.app-header-badge{ display:inline-block; padding:4px 10px; border-radius:999px; background:#E9EDFF; color:#3246D3; font-size:12px; margin-left:8px; vertical-align:middle; }
[data-testid="stChatMessage"]{ border-radius:16px; border:1px solid #E6E8EF; background:#FFF; box-shadow:0 1px 2px rgba(10,14,29,.06); padding:12px 14px; margin:10px 0; }
[data-testid="stChatInput"] textarea{ border-radius:14px !important; border:1px solid #D8DBE6 !important; background:#FFF !important; box-shadow:none !important; font-size:15px; }
[data-testid="stChatInput"] button{ border-radius:12px !important; padding:.5rem .9rem !important; font-weight:600; }
.stButton > button{ border-radius:12px; font-weight:600; padding:.55rem .9rem; border:1px solid #5B7CFA22; box-shadow:0 1px 2px rgba(10,14,29,.06); }
.stMarkdown pre, .stMarkdown code{ font-size:13px !important; border-radius:10px !important; background:#0F172A !important; color:#E2E8F0 !important; }
.stMarkdown ul, .stMarkdown ol { margin-top:.25rem; margin-bottom:.25rem; }
.stMarkdown li { margin:.15rem 0; }
/* Logo oben */
.logo {
    display:flex; align-items:center; gap:10px;
    margin-bottom:0.5rem;
}
.logo img {
    height:38px;
    border-radius:8px;
}
</style>
        """,
        unsafe_allow_html=True,
    )

inject_css()

# --------------------------------------------------------------
# 4️⃣ Titel mit Logo & Badge
# --------------------------------------------------------------
st.markdown(
    f"""
<div class="logo">
  <img src="https://share.google/images/a1pxUdgaPWDw9TCk7" alt="Logo">
  <h1 style="display:inline;">ᾑ AI Kurs-Assistent | Röne Gasser <span class='app-header-badge'>Beta</span></h1>
</div>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------
# 5️⃣ AI-Client Initialisierung
# --------------------------------------------------------------
def init_ai_client():
    """Initialisiert den AI-Client basierend auf verfügbaren API-Schlüsseln."""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not openai_key:
        try: openai_key = st.secrets["OPENAI_API_KEY"]  # type: ignore[index]
        except Exception: pass
    if not anthropic_key:
        try: anthropic_key = st.secrets["ANTHROPIC_API_KEY"]  # type: ignore[index]
        except Exception: pass

    if openai_key:
        try:
            from openai import OpenAI
            return OpenAI(api_key=openai_key), "openai"
        except ImportError:
            st.error("OpenAI-Bibliothek nicht installiert. Bitte über requirements.txt installieren.")
            return None, None

    if anthropic_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=anthropic_key), "anthropic"
        except ImportError:
            st.error("Anthropic-Bibliothek nicht installiert. Bitte über requirements.txt installieren.")
            return None, None

    st.error("Kein API-Schlüssel gefunden! Bitte OPENAI_API_KEY oder ANTHROPIC_API_KEY setzen.")
    return None, None

# --------------------------------------------------------------
# 6️⃣ AI-Abfrage
# --------------------------------------------------------------
def get_ai_response(client, client_type, messages):
    try:
        if client_type == "openai":
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            return resp.choices[0].message.content

        elif client_type == "anthropic":
            system_msg = ""
            user_msgs = []
            for m in messages:
                if m["role"] == "system":
                    system_msg = m["content"]
                else:
                    user_msgs.append({"role": m["role"], "content": m["content"]})

            resp = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                temperature=0.7,
                system=system_msg,
                messages=user_msgs,
            )
            return getattr(resp.content[0], "text", str(resp))
        return "Kein gültiger AI-Client initialisiert."
    except Exception as e:
        return f"Fehler bei der AI-Anfrage: {e}"

# --------------------------------------------------------------
# 7️⃣ Hauptfunktion
# --------------------------------------------------------------
def main():
    """Hauptfunktion der Streamlit-App."""
    st.markdown("*Ihr persönlicher Assistent für den AI Development Kurs*")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Über den Assistenten")
        st.markdown(
            """
Dieser AI-Assistent hilft bei:
- **Kursinhalten** und Konzepten  
- **Übungen** und Aufgaben  
- **Tools** und Technologien  
- **Troubleshooting** bei Problemen  

Stellen Sie einfach Ihre Frage!
"""
        )
        st.header("📅 Kursübersicht")
        st.markdown(
            """
**Abend 1:** Grundlagen & No-Code  
**Abend 2:** Python & Deployment  
**Abend 3:** LangChain & RAG  
**Abend 4:** Fortgeschrittene Konzepte  
**Abend 5:** Eigene Projekte  
**Abend 6:** Präsentationen  
"""
        )

        st.divider()
        st.subheader("🧩 Chat-Verlauf")

        # Chat speichern
        default_name = dt.datetime.now().strftime("chat-%Y%m%d-%H%M%S")
        export_name = st.text_input("Dateiname", value=default_name, key="export_name")
        export_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Verlauf als JSON",
            data=export_json,
            file_name=f"{export_name}.json",
            mime="application/json",
            use_container_width=True,
        )

        # Chat laden
        uploaded = st.file_uploader("Verlauf laden (JSON)", type="json")
        if uploaded is not None:
            try:
                loaded = json.loads(uploaded.read().decode("utf-8"))
                if isinstance(loaded, list) and all(
                    isinstance(x, dict) and "role" in x and "content" in x for x in loaded
                ):
                    st.session_state.messages = loaded
                    st.success("Verlauf geladen.")
                    st.rerun()
                else:
                    st.error("Ungültiges Format: erwartet Liste aus {'role','content'}-Objekten.")
            except Exception as e:
                st.error(f"Konnte Datei nicht laden: {e}")

        # Verlauf löschen
        if st.button("🗑️ Verlauf löschen", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.success("Verlauf gelöscht.")
            st.rerun()

    # Client initialisieren
    client, client_type = init_ai_client()
    if not client:
        st.stop()

    # Chatbereich
    st.header("💬 Stellen Sie Ihre Frage")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("Ihre Frage zum AI Development Kurs…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Denke nach…"):
                ai_messages = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages
                answer = get_ai_response(client, client_type, ai_messages)
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})

    st.markdown("")


# --------------------------------------------------------------
# 8️⃣ Start
# --------------------------------------------------------------
if __name__ == "__main__":
    main()