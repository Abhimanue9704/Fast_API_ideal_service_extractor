from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/download-csv")
def download_csv():
    # Use absolute path or ensure correct working directory
    current_dir = os.getcwd()
    path = os.path.join(current_dir, "data", "service_score_listed.csv")
    
    print(f"Looking for file at: {path}")  # Debug line
    print(f"File exists: {os.path.exists(path)}")  # Debug line
    
    # Check if file exists
    if not os.path.exists(path):
        raise HTTPException(
            status_code=404, 
            detail=f"CSV file not found at {path}. Please run lead scoring first to generate the file."
        )
    
    # Check if file is empty
    if os.path.getsize(path) == 0:
        raise HTTPException(
            status_code=404,
            detail="CSV file is empty. Please run lead scoring to generate data."
        )
    
    return FileResponse(
        path, 
        filename="service_score_listed.csv",
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=service_score_listed.csv"}
    )