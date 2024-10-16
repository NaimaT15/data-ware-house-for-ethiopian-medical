from pydantic import BaseModel
from typing import Optional

class DetectionResultBase(BaseModel):
    channel_name: str
    image: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float
    class_name: str

class DetectionResultCreate(DetectionResultBase):
    pass

class DetectionResultUpdate(BaseModel):
    channel_name: Optional[str] = None
    image: Optional[str] = None
    x_min: Optional[float] = None
    y_min: Optional[float] = None
    x_max: Optional[float] = None
    y_max: Optional[float] = None
    confidence: Optional[float] = None
    class_name: Optional[str] = None

class DetectionResult(DetectionResultBase):
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2.x and above
