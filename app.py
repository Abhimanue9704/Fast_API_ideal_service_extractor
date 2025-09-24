from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from meta_ai_api import MetaAI
import json
import re
            
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
    ai = MetaAI()

    for index, row in df.iterrows():
        rule_score = 0
        ai_points = 0
        role_type=None
        role = row["role"]
        industry = row["industry"]

        # Role relevance
        if role:
            if role.strip().lower() in [r.lower() for r in decision_maker_roles]:
                role_type="decision"
                rule_score += 20
            elif role.strip().lower() in [r.lower() for r in influencer_roles]:
                role_type="influencer"
                rule_score += 10

        # Industry match
        if industry:
            if industry.strip().lower() in [i.lower() for i in offer.ideal_use_cases]:
                rule_score += 20
            elif industry.strip().lower() in [i.lower() for i in adjacent_industries]:
                rule_score += 10

        # Data completeness
        if not row.isnull().any():
            rule_score += 10

        # Example you want the LLM to follow
        example_prompt = """
        User:
        "value_props": ["24/7 outreach", "6x more meetings"],
        "ideal_use_cases": ["B2B SaaS mid-market"]
        Lead: Ava Patel, Head of Growth, FlowMetrics, SaaS, San Francisco, "Helping B2B SaaS companies accelerate pipeline growth with outbound automation, scalable lead generation, and data-driven campaigns that deliver results within weeks."
        Role_type: Decision

        Assistant:
        "intent": "High"
        "reasoning": "Fits ICP SaaS mid-market and role is decision maker."
        """

        # Current row info you want to classify
        row_info = row.to_dict()  # assuming row is a pandas Series

        prompt = f"""
        {example_prompt}

        Now classify this lead:

        User:
        "value_props": {offer.value_props},
        "ideal_use_cases": {offer.ideal_use_cases}
        Lead: {row_info["name"]}, {row_info["role"]}, {row_info["company"]}, {row_info["industry"]}, {row_info["location"]}, "{row_info["linkedin_bio"]}"
        Decision: {role_type}

        Assistant:
        """

        response = ai.prompt(message=prompt)
        llm_message = response.get("message", "")
        print(llm_message)

        # Extract intent
        intent_match = re.search(r'"intent"\s*:\s*"(\w+)"', llm_message)
        intent = intent_match.group(1) if intent_match else "Unknown"

        # Extract reasoning
        reasoning_match = re.search(r'"reasoning"\s*:\s*"(.+?)"', llm_message, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else llm_message

        # Assign AI points
        if intent.lower() == "high":
            ai_points += 50
        elif intent.lower() == "medium":
            ai_points += 30
        else:
            ai_points += 10

    
        results.append({
            "name": row["name"],
            "role": row["role"],
            "company": row["company"],
            "intent" : intent,
            "score" : rule_score+ai_points,
            "reasoning" : reasoning
        })

    res=pd.DataFrame(results)
    res.to_csv("service_score_listed.csv",index=False)
    
