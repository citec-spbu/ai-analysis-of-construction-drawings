# app/agent.py
import os
import time
from typing import Dict, Optional
from omegaconf import DictConfig
from langchain_core.messages import HumanMessage, AIMessage
from app.graph import build_graph
from app.monitoring import init_clearml, close_clearml, log_question_answer, log_cache_operation
from app.tools import set_current_drawing
from app.drawing_cache import DrawingKnowledgeManager
from app.cache import AgentCache


class DrawingAgent:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.graph = build_graph(cfg)
        init_clearml()
        self.stats = {"questions": 0, "total_time": 0, "errors": 0}

        # Менеджер знаний чертежа (кеш и RAG на основе истории)
        self.drawing_knowledge = DrawingKnowledgeManager()

        # Кеш ответов (для идентичных запросов)
        self.cache = AgentCache()

    async def run(self, path: str, question: str, wait_time: Optional[int] = None,
                  max_retries: Optional[int] = None, thread_id: Optional[str] = None,
                  page: int = 0) -> Dict:
        start_time = time.time()
        # настройки по умолчанию...
        cache_key = f"{thread_id}:{path}:{page}:{question}"

        # Проверка кеша ответов
        cached = self.cache.get(cache_key)
        if cached:
            log_cache_operation("get", cache_key, True)
            return cached

        log_cache_operation("get", cache_key, False)

        try:
            # Загрузка чертежа с кешированием (тяжёлые операции только при первом обращении)
            drawing_data = self.drawing_knowledge.load_drawing_and_cache(path, page)
            image_base64 = drawing_data["image_base64"]
            ocr_text = drawing_data.get("ocr_text", "")
            width = drawing_data["width"]
            height = drawing_data["height"]

            set_current_drawing(image_base64)

            # Инициализация статической базы знаний (если индекс пуст)
            self.drawing_knowledge.initialize_static_knowledge(path, page, drawing_data)

            # Получаем контекст из истории + статики
            rag_context = self.drawing_knowledge.retrieve_context(path, page, question)

            # Собираем начальное состояние
            initial_state = {
                "messages": [HumanMessage(content=question)],
                "current_drawing": image_base64,
                "drawing_width": width,
                "drawing_height": height,
                "page": page,
                "ocr_text": ocr_text,
                "context": rag_context,
                # ... остальные поля состояния
            }

            # Вызов графа
            result = await self.graph.ainvoke(initial_state, config=config)

            # Извлечение ответа
            answer = self._extract_answer(result)

            # Сохраняем взаимодействие в индекс чертежа
            if answer:
                self.drawing_knowledge.add_interaction_to_index(path, page, question, answer)

            response_time = time.time() - start_time
            self.stats["questions"] += 1
            self.stats["total_time"] += response_time
            log_question_answer(question, answer, True, response_time)

            final = {"success": True, "answer": answer, "error": None}

            # Кеш ответа
            self.cache.set(cache_key, final)
            log_cache_operation("set", cache_key, True)
            return final

        except Exception as e:
            # обработка ошибки...
            pass

    def close(self):
        self.cache.flush_to_log()
        close_clearml()