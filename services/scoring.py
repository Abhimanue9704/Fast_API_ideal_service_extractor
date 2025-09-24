import pandas as pd
import re
from meta_ai_api import MetaAI

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

def score_leads(df: pd.DataFrame, offer) -> pd.DataFrame:
    ai = MetaAI()
    results = []

    for _, row in df.iterrows():
        rule_score = 0
        ai_points = 0
        role_type = None
        role = row.get("role", "")
        industry = row.get("industry", "")

        # Role relevance
        if role:
            if role.strip().lower() in [r.lower() for r in decision_maker_roles]:
                role_type = "decision"
                rule_score += 20
            elif role.strip().lower() in [r.lower() for r in influencer_roles]:
                role_type = "influencer"
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

        # AI prompt
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

        row_info = row.to_dict()
        prompt = f"""
        {example_prompt}

        Now classify this lead:

        User:
        "value_props": {offer.value_props},
        "ideal_use_cases": {offer.ideal_use_cases}
        Lead: {row_info.get("name")}, {row_info.get("role")}, {row_info.get("company")}, {row_info.get("industry")}, {row_info.get("location")}, "{row_info.get("linkedin_bio")}"
        Decision: {role_type}

        Assistant:
        """

        response = ai.prompt(message=prompt)
        llm_message = response.get("message", "")

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
            "name": row.get("name"),
            "role": row.get("role"),
            "company": row.get("company"),
            "intent": intent,
            "score": rule_score + ai_points,
            "reasoning": reasoning
        })

    res_df = pd.DataFrame(results)
    res_df.to_csv("data/service_score_listed.csv", index=False)
    return res_df
