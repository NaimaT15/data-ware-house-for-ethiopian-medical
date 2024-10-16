import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# models.py
from sqlalchemy import Column, Integer, String, Float
from my_fastapi.database import Base

class DetectionResult(Base):
    __tablename__ = 'detection_results'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    channel_name = Column(String, nullable=False, index=True)
    image = Column(String, nullable=False)
    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    y_max = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    class_name = Column(String, nullable=False, index=True)