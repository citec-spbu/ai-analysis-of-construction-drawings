import asyncio
import hydra
from omegaconf import DictConfig
from dotenv import load_dotenv
import logging 
from app.agent import DrawingAgent

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

@hydra.main(config_path="config", config_name="config", version_base=None)
def main(cfg: DictConfig):
    asyncio.run(async_main(cfg))


async def async_main(cfg: DictConfig):
    agent = DrawingAgent(cfg)
    drawing_path = input("\nПуть к чертежу (PDF/PNG/JPG): ").strip()
    
    thread_id = cfg.run.thread_id if hasattr(cfg, 'run') else "drawing_session_1"
    
    print("\nДля выхода: q, quit, exit\n")
    
    try:
        while True:
            question = input("Вопрос: ").strip()
            
            if question.lower() in ["q", "quit", "exit"]:
                print("\nДо свидания!")
                break
            
            if not question:
                continue
            
            print("\nАссистент анализирует...")
            
            result = await agent.run(
                path=drawing_path,
                question=question,
                wait_time=cfg.agent.wait_time if hasattr(cfg, 'agent') else 4,
                thread_id=thread_id
            )
            
            if result["success"]:
                print(f"ОТВЕТ:\n{result['answer']}")
            else:
                print(f"ОШИБКА:\n{result['error']}")
    except KeyboardInterrupt:
        print("\n\n Прервано пользователем")
    finally:
        agent.close()

if __name__ == "__main__":
    main()