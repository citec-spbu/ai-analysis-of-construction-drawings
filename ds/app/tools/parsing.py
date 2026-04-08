import re


def extract_dimensions(text: str):
    """
    Извлекает размеры типа Ø25, 100мм и т.д.
    """

    pattern = r"(Ø?\d+\.?\d*)\s?(mm|cm|m)?"
    matches = re.findall(pattern, text)

    return [
        {
            "value": float(m[0].replace("Ø", "")),
            "unit": m[1] or "mm"
        }
        for m in matches
    ]


def extract_objects(text: str):
    """
    Примитивное извлечение объектов
    """

    objects = []

    if "Ø" in text:
        objects.append({"type": "dimension"})

    if "line" in text.lower():
        objects.append({"type": "line"})

    return objects


def extract_relationships(objects: list):
    """
    Связи между объектами
    """

    relationships = []

    if len(objects) > 1:
        relationships.append({
            "source_id": "1",
            "target_id": "2",
            "type": "connected"
        })

    return relationships