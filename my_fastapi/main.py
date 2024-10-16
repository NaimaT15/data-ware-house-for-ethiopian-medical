import sys
import os

# Adjust this path to the root of your project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from my_fastapi import crud, models, schemas
from my_fastapi.database import Base, get_db, engine

# Initialize FastAPI app
app = FastAPI()

# Create all database tables (Move this to a dedicated setup script if needed)
Base.metadata.create_all(bind=engine)

# Route to get detection results
@app.get("/detection-results/", response_model=list[schemas.DetectionResult])
def read_detection_results(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        detection_results = crud.get_detection_results(db, skip=skip, limit=limit)
        return detection_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching detection results: {str(e)}")

# Route to create new detection result
@app.post("/detection-results/", response_model=schemas.DetectionResult)
def create_detection_result(detection: schemas.DetectionResultCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_detection_result(db=db, detection=detection)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating detection result: {str(e)}")

# Route to update a detection result
# Correct usage in main.py (for updating a detection result):
@app.put("/detection-results/{detection_id}", response_model=schemas.DetectionResult)
def update_detection_result(detection_id: int, update_data: schemas.DetectionResultUpdate, db: Session = Depends(get_db)):
    detection = crud.get_detection_result_by_id(db, detection_id)  # Corrected function name
    if not detection:
        raise HTTPException(status_code=404, detail="Detection result not found")
    updated_detection = crud.update_detection_result(db, detection_id, update_data)
    return updated_detection

# Route to delete a detection result
@app.delete("/detection-results/{detection_id}", response_model=dict)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    success = crud.delete_detection_result(db, detection_id)
    if not success:
        raise HTTPException(status_code=404, detail="Detection result not found")
    return {"message": "Detection result deleted successfully"}