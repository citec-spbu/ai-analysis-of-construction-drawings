def build_instructor_input(state):

    ocr = state.get("ocr_text", "")
    context = state.get("context", "")
    page = state.get("page", "unknown")

    messages = state.get("messages", [])

    last_message = ""
    if messages:
        for msg in reversed(messages):
            if hasattr(msg, "content") and isinstance(msg.content, str):
                last_message = msg.content
                break

    return f"""
Ты получаешь данные анализа инженерного чертежа.

Страница: {page}

[OCR]
{ocr}

[Контекст]
{context}

[Анализ агента]
{last_message}

Используй только эти данные.
"""