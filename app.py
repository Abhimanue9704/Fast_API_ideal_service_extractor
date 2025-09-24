from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd

df = pd.read_csv("leads_30.csv")

app = FastAPI()

class Offer(BaseModel):
    name: str
    value_props: List[str]
    ideal_use_cases: List[str]

decision_maker_roles = [
    "CEO", "Chief Executive Officer", "Founder", "President",
    "VP Sales", "VP Marketing", "Head of Growth", "Managing Director",
    "Chief Strategy Officer", "VP Business Development"
]

influencer_roles = [
    "Marketing Manager", "Product Manager", "Sales Manager",
    "Operations Lead", "Marketing Specialist", "Growth Marketing Lead",
    "Head of Partnerships", "Head of Customer Success",
    "Product Marketing Manager", "Marketing Director"
]

adjacent_industries = ["FinTech", "AI SaaS", "Consulting", "Software", "Cloud", "Technology"]

required_fields = ["name", "role", "company", "industry", "location", "linkedin_bio"]

@app.post("/offer")
async def offer(offer: Offer):
    results = []

    for index, row in df.iterrows():
        points = 0
        role = row["role"]
        industry = row["industry"]

        # Role relevance
        if role:
            if role.strip().lower() in [r.lower() for r in decision_maker_roles]:
                points += 20
            elif role.strip().lower() in [r.lower() for r in influencer_roles]:
                points += 10

        # Industry match
        if industry:
            if industry.strip().lower() in [i.lower() for i in offer.ideal_use_cases]:
                points += 20
            elif industry.strip().lower() in [i.lower() for i in adjacent_industries]:
                points += 10

        # Data completeness
        if not row.isnull().any():
            points += 10

        results.append({
            "name": row["name"],
            "role": role,
            "company": row["company"],
            "industry": industry,
            "rule_score": points
        })

    return results
