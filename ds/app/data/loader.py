from pdf2image import convert_from_path
from PIL import Image
import os


from pdf2image import convert_from_path
from PIL import Image
import os


def load_drawing(path: str):
    """
    Загружает PDF (все страницы) или изображение
    Возвращает список изображений
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    path_lower = path.lower()

    # PDF → ВСЕ страницы
    if path_lower.endswith(".pdf"):
        images = convert_from_path(path)
        return images  # список!

    # Image → оборачиваем в список
    elif path_lower.endswith((".jpg", ".jpeg", ".png")):
        return [Image.open(path)]

    else:
        raise ValueError(f"Unsupported format: {path}")

def load_dataset(dataset_path: str):
    """
    Загружает список файлов из датасета
    """

    files = os.listdir(dataset_path)

    pdf_files = [f for f in files if f.lower().endswith(".pdf")]
    img_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    return {
        "pdf": pdf_files,
        "images": img_files
    }