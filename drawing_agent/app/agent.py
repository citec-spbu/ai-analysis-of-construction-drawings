# app/agent.py - используем preprocess_image из data
import os
import time
from typing import Dict, Optional
from PIL import Image
from omegaconf import DictConfig
from langchain_core.messages import HumanMessage, AIMessage

from app.graph import build_graph
from app.monitoring import init_clearml, close_clearml, log_question_answer
from app.tools import set_current_drawing
from app.data.loader import load_drawing
from app.data.preprocess import preprocess_image  # используем существующую функцию


class DrawingAgent:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg
        self.graph = build_graph(cfg)
        init_clearml()
        self.stats = {
            "questions": 0,
            "total_time": 0,
            "errors": 0
        }

    async def run(
        self, 
        path: str, 
        question: str, 
        wait_time: Optional[int] = None,
        max_retries: Optional[int] = None,
        thread_id: Optional[str] = None,
        page: int = 0
    ) -> Dict:
        start_time = time.time()
        
        wait_time = wait_time or (self.cfg.agent.get('wait_time', 4) if hasattr(self.cfg, 'agent') else 4)
        max_retries = max_retries or (self.cfg.agent.get('max_retries', 4) if hasattr(self.cfg, 'agent') else 4)
        thread_id = thread_id or (self.cfg.run.get('thread_id', 'default') if hasattr(self.cfg, 'run') else 'default')
        
        try:
            if not os.path.exists(path):
                error_msg = f"Файл не найден: {path}"
                log_question_answer(question, None, False)
                return {
                    "success": False,
                    "error": error_msg,
                    "answer": None
                }
            images = load_drawing(path)
            
            if page >= len(images):
                page = 0
            
            image = images[page]
            processed = preprocess_image(image)
            image_base64 = processed["image_base64"]
            set_current_drawing(image_base64)
            
            config = {"configurable": {"thread_id": thread_id}}
            
            initial_state = {
                "messages": [HumanMessage(content=question)],
                "current_drawing": image_base64,
                "drawing_width": image.width,
                "drawing_height": image.height,
                "page": page,
                "ocr_text": processed.get("ocr_text", ""),
                "context": "",
                "tool_results": {},
                "extracted_holes": [],
                "extracted_dimensions": {},
                "extracted_tables": [],
                "extracted_objects": [],
                "text_dimensions": [],
                "gost_results": [],
                "metadata_retrieved": False,
                "analysis_complete": False,
                "wait_time": wait_time,
                "max_retries": max_retries,
                "final_output": None
            }
            
            result = await self.graph.ainvoke(initial_state, config=config)
            
            answer = None
            if result.get("messages"):
                for msg in reversed(result["messages"]):
                    if isinstance(msg, AIMessage) and msg.content:
                        answer = msg.content
                        break
            
            if result.get("final_output"):
                answer = f"{answer}\n\nСтруктурированные данные:\n{result['final_output']}"
            
            response_time = time.time() - start_time
            self.stats["questions"] += 1
            self.stats["total_time"] += response_time
            
            log_question_answer(question, answer, True, response_time)
            
            return {
                "success": True,
                "answer": answer or "Не удалось получить ответ",
                "error": None,
                "structured_output": result.get("final_output")
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            error_msg = str(e)
            self.stats["errors"] += 1
            
            log_question_answer(question, None, False, response_time)
            
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": error_msg,
                "answer": None,
                "structured_output": None
            }
    
    def close(self):
        close_clearml()