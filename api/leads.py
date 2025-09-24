from fastapi import APIRouter, UploadFile, File
import shutil

router = APIRouter()

@router.post("/leads/upload")
async def upload(file: UploadFile = File(...)):
    file_location = "data/services.csv"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"info": f"File saved at {file_location}"}
