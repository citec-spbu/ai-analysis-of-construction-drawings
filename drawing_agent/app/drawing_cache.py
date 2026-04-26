import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from datetime import datetime

from rag.embeddings import EmbeddingGenerator
from rag.vectors import VectorStore
from app.data.loader import load_drawing
from app.data.preprocess import preprocess_image

class DrawingKnowledgeManager:
    def __init__(self, cache_dir: str = "cache/drawings"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.embedder = EmbeddingGenerator()
        self._indices: Dict[str, VectorStore] = {}
        self._static_cache: Dict[str, Dict] = {}

    def _get_drawing_hash(self, path: str, page: int) -> str:
        raw = f"{path}:{page}"
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_index_paths(self, hash_id: str):
        base = self.cache_dir / hash_id
        return str(base) + "_index.bin", str(base) + "_metadata.pkl"

    def _get_static_cache_path(self, hash_id: str):
        return self.cache_dir / f"{hash_id}_static.json"

    def load_drawing_and_cache(self, path: str, page: int = 0) -> Dict[str, Any]:
        hash_id = self._get_drawing_hash(path, page)

        # 1. Проверка статического кеша
        static_cache_path = self._get_static_cache_path(hash_id)
        if static_cache_path.exists():
            with open(static_cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            # Загружаем изображение для текущего использования (лёгкая операция)
            images = load_drawing(path)
            image = images[page]
            processed = {"image_base64": cached["image_base64"],
                         "ocr_text": cached["ocr_text"],
                         "width": image.width, "height": image.height}
            return processed

        # 2. Полная обработка
        images = load_drawing(path)
        if page >= len(images):
            page = 0
        image = images[page]
        processed = preprocess_image(image)

        # Сохраняем статический кеш
        cache_data = {
            "image_base64": processed["image_base64"],
            "ocr_text": processed.get("ocr_text", ""),
            "extracted_holes": [],    # эти данные можно заполнять при более глубоком анализе
            "extracted_dimensions": {},
            "extracted_tables": [],
            "extracted_objects": [],
            "timestamp": datetime.now().isoformat()
        }
        with open(static_cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

        return {"image_base64": cache_data["image_base64"],
                "ocr_text": cache_data["ocr_text"],
                "width": image.width, "height": image.height}

    def get_or_create_index(self, path: str, page: int) -> VectorStore:
        hash_id = self._get_drawing_hash(path, page)
        if hash_id in self._indices:
            return self._indices[hash_id]

        index_path, meta_path = self._get_index_paths(hash_id)
        store = VectorStore(index_path=index_path, metadata_path=meta_path)
        self._indices[hash_id] = store
        return store

    def initialize_static_knowledge(self, path: str, page: int, static_data: Dict[str, Any]):
        """Добавляет статическую информацию в индекс, если он пуст."""
        store = self.get_or_create_index(path, page)
        if store.index.ntotal == 0:
            # Формируем текстовые фрагменты из статических данных
            fragments = []
            if static_data.get("ocr_text"):
                fragments.append(f"Распознанный текст чертежа: {static_data['ocr_text']}")
            # Можно добавить размеры, объекты и т.д.
            for frag in fragments:
                emb = self.embedder.generate(frag)
                store.add(frag, emb.tolist())  # метод add ожидает текст и embedding

    def add_interaction_to_index(self, path: str, page: int, question: str, answer: str):
        """Сохраняет вопрос и ответ в индекс чертежа."""
        store = self.get_or_create_index(path, page)
        combined = f"Вопрос: {question}\nОтвет: {answer}"
        emb = self.embedder.generate(combined)
        store.add(combined, emb.tolist())
        # Дополнительно пишем в сессионный лог
        hash_id = self._get_drawing_hash(path, page)
        log_path = self.cache_dir / f"{hash_id}_sessions.jsonl"
        with open(log_path, "a", encoding="utf-8") as f:
            record = {"timestamp": datetime.now().isoformat(), "question": question, "answer": answer}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def retrieve_context(self, path: str, page: int, query: str, top_k: int = 4) -> str:
        """Извлекает релевантные фрагменты из истории и статики."""
        store = self.get_or_create_index(path, page)
        if store.index.ntotal == 0:
            return ""
        query_emb = self.embedder.generate(query)
        results = store.search(query_emb.tolist(), top_k)
        if not results:
            return ""
        return "\n\n".join([doc for doc, _ in results])