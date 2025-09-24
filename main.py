from fastapi import FastAPI
from api import offer, leads,download_csv

app = FastAPI()

app.include_router(offer.router)
app.include_router(leads.router)
app.include_router(download_csv.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
