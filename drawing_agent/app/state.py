from typing import TypedDict, Annotated, List, Any,Optional, Dict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from omegaconf import DictConfig

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    current_drawing: Optional[str]
    drawing_width: int
    drawing_height: int
    page: int  
    ocr_text: str 
    context: str 
    extracted_holes: List[Dict]
    extracted_dimensions: Dict
    extracted_objects: List[Dict]
    analysis_complete: bool
    wait_time: int
    max_retries: int
    final_output: Optional[Dict[str,Any]]
    drawing_context: Optional[str]
