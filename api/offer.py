from fastapi import APIRouter
from models.offer_model import Offer
from services.scoring import score_leads
import pandas as pd

router = APIRouter()

@router.post("/offer")
async def offer_endpoint(offer: Offer):
    df = pd.read_csv("data/services.csv")  # Uploaded leads
    result_df = score_leads(df, offer)
    return result_df.to_dict(orient="records")
