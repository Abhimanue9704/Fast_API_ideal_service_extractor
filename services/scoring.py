from groq import Client
import os
import re
import pandas as pd

groq_api_key = os.environ.get("GROQ_API_KEY")
client = Client(api_key=groq_api_key)

class Offer:
    def __init__(self, value_props, ideal_use_cases):
        self.value_props = value_props
        self.ideal_use_cases = ideal_use_cases

# Your rule scoring logic
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

        # Compose prompt per lead
        row_info = row.to_dict()
        prompt = f"""
        Classify this lead's intent and provide concise reasoning.

        Value Props: {offer.value_props}
        Ideal Use Cases: {offer.ideal_use_cases}
        
        Lead: {row_info.get("name", "")}, {row_info.get("role", "")}, {row_info.get("company", "")}, {row_info.get("industry", "")}, {row_info.get("location", "")}, "{row_info.get("linkedin_bio", "")}"
        Role Type: {role_type}

        Respond in exactly this format:
        "intent": "High"
        "reasoning": "Brief reason here"

        Example:
        "intent": "High"
        "reasoning": "Fits ideal use case of B2B SaaS mid-market and has a decision-making role"
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )
            llm_message = response.choices[0].message.content

            # Extract intent & reasoning with better regex
            intent_match = re.search(r'"intent"\s*:\s*"([^"]+)"', llm_message)
            intent = intent_match.group(1) if intent_match else "Unknown"
            
            reasoning_match = re.search(r'"reasoning"\s*:\s*"([^"]+)"', llm_message)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"

            # Clean up reasoning
            reasoning = reasoning.replace('\\n', ' ').replace('\n', ' ').strip()
            
        except Exception as e:
            print(f"Error processing lead {row.get('name', 'Unknown')}: {e}")
            intent = "Unknown"
            reasoning = "Error in processing"

        # Assign AI points based on intent
        if intent.lower() == "high":
            ai_points += 50
        elif intent.lower() == "medium":
            ai_points += 30
        else:
            ai_points += 10

        total_score = rule_score + ai_points

        results.append({
            "name": row.get("name", ""),
            "role": row.get("role", ""),
            "company": row.get("company", ""),
            "intent": intent,
            "score": total_score,
            "reasoning": reasoning
        })

    res_df = pd.DataFrame(results)
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    res_df.to_csv("data/service_score_listed.csv", index=False)
    return res_df

# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = {
        'name': ['Ava Patel', 'John Smith', 'Sarah Johnson'],
        'role': ['Head of Growth', 'Software Engineer', 'VP of Sales'],
        'company': ['FlowMetrics', 'TechCorp', 'SalesForce'],
        'industry': ['SaaS', 'Software', 'CRM'],
        'location': ['San Francisco', 'New York', 'Austin'],
        'linkedin_bio': [
            'Helping B2B SaaS companies accelerate pipeline growth...',
            'Full-stack developer passionate about clean code...',
            'Sales leader with 10+ years in enterprise software...'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Define offer
    offer = Offer(
        value_props=["24/7 outreach", "6x more meetings"],
        ideal_use_cases=["B2B SaaS mid-market"]
    )
    
    # Score leads
    result = score_leads(df, offer)
    print(result)