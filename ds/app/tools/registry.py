from langchain_core.tools import tool

from app.tools.vision import extract_text_from_image
from app.tools.parsing import (
    extract_dimensions,
    extract_objects,
    extract_relationships,
)
from app.tools.rag import search_context

@tool
def extract_text(image_base64: str) -> str:
    """Извлекает текст из изображения"""
    return extract_text_from_image(image_base64)


@tool
def extract_dims(text: str) -> list:
    """Извлекает размеры из текста"""
    return extract_dimensions(text)


@tool
def detect_objects(text: str) -> list:
    """Определяет объекты чертежа"""
    return extract_objects(text)


@tool
def detect_relationships(objects: list) -> list:
    """Определяет связи между объектами"""
    return extract_relationships(objects)


@tool
def search_standards(query: str) -> str:
    """Поиск по стандартам (RAG)"""
    return search_context(query)

def create_tools():
    """
    Возвращает dict tools для агента
    """

    tools = [
        extract_text,
        extract_dims,
        detect_objects,
        detect_relationships,
        search_standards,
    ]

    # важно: агент ожидает dict
    return {tool.name: tool for tool in tools}