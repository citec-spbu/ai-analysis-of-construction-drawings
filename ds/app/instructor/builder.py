def build_instructor_input(state):
    ocr = state.get("ocr_text", "")
    context = state.get("context", "")
    messages = state.get("messages", [])

    last_message = ""
    if messages:
        last_message = messages[-1].content

    return f"""
OCR:
{ocr}

Контекст (RAG):
{context}

Анализ агента:
{last_message}
"""