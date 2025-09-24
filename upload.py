from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

@app.post("/leads/upload")
async def upload(file: UploadFile = File(...)):
    file_location = "services.csv"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"info": f"File saved at {file_location}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("upload:app", host="0.0.0.0", port=8001, reload=True)
