import sys
import os


# Ensure the root path is correctly set
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy.orm import Session
from my_fastapi import models, schemas
def get_detection_results(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of detection results with pagination.
    """
    return db.query(models.DetectionResult).offset(skip).limit(limit).all()

def get_detection_result_by_id(db: Session, detection_id: int):
    """
    Retrieve a single detection result by its ID.
    """
    return db.query(models.DetectionResult).filter(models.DetectionResult.id == detection_id).first()

def create_detection_result(db: Session, detection: schemas.DetectionResultCreate):
    """
    Create a new detection result entry.
    """
    db_detection = models.DetectionResult(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

def update_detection_result(db: Session, detection_id: int, update_data: schemas.DetectionResultUpdate):
    """
    Update an existing detection result by its ID.
    """
    db_detection = get_detection_result_by_id(db, detection_id)
    if not db_detection:
        return None
    
    # Update the fields with the new data
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_detection, key, value)
    
    db.commit()
    db.refresh(db_detection)
    return db_detection

def delete_detection_result(db: Session, detection_id: int):
    """
    Delete a detection result by its ID.
    """
    db_detection = get_detection_result_by_id(db, detection_id)
    if db_detection:
        db.delete(db_detection)
        db.commit()
        return True
    return False
