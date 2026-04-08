import base64
from io import BytesIO
from PIL import Image
import numpy as np
import easyocr


reader = easyocr.Reader(['ru', 'en'], gpu=False)


def extract_text_from_image(image_base64: str) -> str:

    try:
        # 1. base64 → bytes
        image_bytes = base64.b64decode(image_base64)

        # 2. bytes → PIL
        image = Image.open(BytesIO(image_bytes)).convert("RGB")

        # 3. PIL → numpy (нужно для easyocr)
        image_np = np.array(image)

        # 4. OCR
        results = reader.readtext(
            image_np,
            detail=1,        # получаем bbox + текст + confidence
            paragraph=False
        )

        # 5. собираем текст
        texts = []
        for bbox, text, confidence in results:
            if confidence > 0.4:  # фильтр шума
                texts.append(text)

        # 6. финальный текст
        return "\n".join(texts)

    except Exception as e:
        return f"OCR error: {str(e)}"