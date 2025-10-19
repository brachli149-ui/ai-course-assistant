"""
Wissensbasis für den AI Development Kurs-Assistenten
"""

COURSE_KNOWLEDGE = """
# AI Development Kurs - Wissensbasis

## Kursübersicht
Der AI Development Kurs umfasst 6 Abende mit je 4 Lektionen (50 Min + 10 Min Pause).

### Abend 1: Grundlagen und No-Code Tools
- Einführung in AI/ML Konzepte
- No-Code/Low-Code AI-Plattformen
- Flowise und Langflow
- Praktische Übungen mit AI-Tools

### Abend 2: Python Setup und Deployment
- Python-Entwicklungsumgebung einrichten
- Git/GitHub Grundlagen
- Streamlit AI-Anwendungen entwickeln
- Erstes Deployment auf Streamlit Cloud
- Einführung in Vektordatenbanken

### Abend 3: LangChain und RAG
- LangChain Framework
- Retrieval Augmented Generation (RAG)
- Vector Stores und Embeddings
- Praktische RAG-Implementierung

### Abend 4: Fortgeschrittene Konzepte
- Erweiterte LangChain Patterns
- Multi-Agent Systeme
- Performance Optimierung

### Abend 5: Eigene Projekte
- Projektplanung und -umsetzung
- Individuelle Betreuung
- Code Reviews

### Abend 6: Präsentationen
- Projektpräsentationen
- Feedback und Diskussion
- Ausblick und Weiterbildung

## Wichtige Konzepte
### Large Language Models (LLMs)
- GPT-4, Claude, Gemini
- Prompt Engineering
- API-Integration

### Vector Stores
- Speicherung von Embeddings
- Similarity Search
- FAISS, ChromaDB, Pinecone

### Embeddings
- Text-zu-Vektor Transformation
- Semantische Ähnlichkeit
- OpenAI Embeddings, Sentence Transformers

### RAG (Retrieval Augmented Generation)
- Kombination von Retrieval und Generation
- Kontextuelle Antworten
- Wissensbasis-Integration

## Tools und Technologien
- Python, Streamlit
- LangChain, OpenAI API
- Git/GitHub
- Flowise, Langflow
- Vector Databases

## Links und URL zum Kurs
# - https://share.streamlit.io/
# - https://github.com/
# - https://platform.openai.com/api-keys
"""



def get_system_prompt():
    """Erstellt den System-Prompt für den AI Assistenten"""
    return f"""Du bist ein hilfreicher AI-Assistent für den AI Development Kurs.
Deine Aufgabe ist es, Fragen der Kursteilnehmer zu beantworten basierend auf folgender
Wissensbasis:
{COURSE_KNOWLEDGE}
Antworte immer:
- Freundlich und hilfsbereit
- Auf Deutsch
- Präzise und verständlich
- Mit praktischen Beispielen wenn möglich
- Ehrlich, wenn du etwas nicht weisst
Wenn eine Frage nicht direkt mit dem Kurs zusammenhängt, verweise höflich auf den
Kurskontext zurück.
"""