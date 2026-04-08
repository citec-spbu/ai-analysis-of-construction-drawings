from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Dimension(BaseModel):
    value: float
    unit: Literal["mm", "cm", "m", "inch"]
    dimension_type: str
    description: str
    between_objects: Optional[List[str]] = None


class DrawingObject(BaseModel):
    id: str
    type: str
    description: str
    dimensions: List[Dimension] = Field(default_factory=list)
    annotations: List[str] = Field(default_factory=list)


class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str


class DrawingAnalysis(BaseModel):
    objects: List[DrawingObject]
    relationships: List[Relationship]