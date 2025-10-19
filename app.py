import os
import streamlit as st
from dotenv import load_dotenv
from course_knowledge import get_system_prompt

# .env laden (falls vorhanden)
load_dotenv()

# Streamlit-Seite konfigurieren
st.set_page_config(
    page_title="AI Kurs-Assistent",
    page_icon="ᾑ",
    layout="wide",
    initial_sidebar_state="expanded",
)

def init_ai_client():
    """Initialisiert den AI-Client basierend auf verfuegbaren API-Schluesseln."""
    # 1) Zuerst aus Umgebungsvariablen / .env lesen
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # 2) Optional st.secrets nur versuchen, wenn noch kein Key da ist
    if not openai_key:
        try:
            openai_key = st.secrets["OPENAI_API_KEY"]
        except Exception:
            pass
    if not anthropic_key:
        try:
            anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            pass

    # 3) Client initialisieren
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            return client, "openai"
        except ImportError:
            st.error("OpenAI-Bibliothek nicht installiert. Bitte ueber requirements.txt installieren.")
            return None, None

    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            return client, "anthropic"
        except ImportError:
            st.error("Anthropic-Bibliothek nicht installiert. Bitte ueber requirements.txt installieren.")
            return None, None

    st.error("Kein API-Schluessel gefunden! Bitte OPENAI_API_KEY oder ANTHROPIC_API_KEY setzen.")
    return None, None


def get_ai_response(client, client_type, messages):
    """Sendet Anfrage an den gewaehlten AI-Service und gibt die Antwort zurueck."""
    try:
        if client_type == "openai":
            # messages: Liste von {"role": "system"|"user"|"assistant", "content": str}
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7,
            )
            return resp.choices[0].message.content

        elif client_type == "anthropic":
            # Anthropic erwartet system separat, messages ohne "system"
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
            # erste Text-Antwort zurueckgeben
            return getattr(resp.content[0], "text", str(resp))

        else:
            return "Kein gueltiger AI-Client initialisiert."

    except Exception as e:
        return f"Fehler bei der AI-Anfrage: {e}"


def main():
    """Hauptfunktion der Streamlit-App."""
    # Header
    st.title("ᾑ AI Kurs-Assistent")
    st.markdown("*Ihr persoenlicher Assistent fuer den AI Development Kurs*")

    # Sidebar
    with st.sidebar:
        st.header("ℹ️ Ueber den Assistenten")
        st.markdown(
            """
Dieser AI-Assistent hilft bei:
- **Kursinhalten** und Konzepten  
- **Uebungen** und Aufgaben  
- **Tools** und Technologien  
- **Troubleshooting** bei Problemen  

Stellen Sie einfach Ihre Frage!
"""
        )
        st.header("📅 Kursuebersicht")
        st.markdown(
            """
**Abend 1:** Grundlagen & No-Code  
**Abend 2:** Python & Deployment  
**Abend 3:** LangChain & RAG  
**Abend 4:** Fortgeschrittene Konzepte  
**Abend 5:** Eigene Projekte  
**Abend 6:** Praesentationen  
"""
        )

    # AI-Client initialisieren
    client, client_type = init_ai_client()
    if not client:
        st.stop()

    # Chat-Interface
    st.header("💬 Stellen Sie Ihre Frage")

    # Session State fuer Chat-Verlauf
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat-Verlauf anzeigen
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Neue Nachricht
    prompt = st.chat_input("Ihre Frage zum AI Development Kurs...")
    if prompt:
        # Nutzerfrage merken & anzeigen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Antwort erzeugen
        with st.chat_message("assistant"):
            with st.spinner("Denke nach..."):
                ai_messages = [{"role": "system", "content": get_system_prompt()}] + st.session_state.messages
                answer = get_ai_response(client, client_type, ai_messages)
                st.markdown(answer)

        # Antwort im Verlauf speichern
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # Reset-Button
    if st.button("🔄 Chat zuruecksetzen"):
        st.session_state.messages = []
        st.rerun()


if __name__ == "__main__":
    main()