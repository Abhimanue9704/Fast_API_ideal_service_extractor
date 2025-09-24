# AI Lead Scoring Service

A FastAPI service to score leads using **rule-based logic** combined with **AI scoring** via Groq LLaMA models. This project is designed to demonstrate clean, well-structured code with proper documentation and commit history.

---

## Repository Guidelines

* Proper GitHub repository with meaningful commit history (no single-commit dumps)
* Well-structured code:
  * `api/` → FastAPI endpoints (leads.py, offer.py, download_csv.py)
  * `services/` → scoring logic
  * `data/` → CSV inputs and outputs
* Inline comments and docstrings explaining logic and API behavior
* All setup, usage, and rule explanations documented in this README

---

## Setup Steps

1. Clone the repository:

```bash
git clone https://github.com/Abhimanue9704/Fast_API_ideal_service_extractor.git
cd Fast_API_ideal_service_extractor
```

2. Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate  # Linux/macOS
env\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set Groq API key as an environment variable:

```bash
# Linux/macOS
export GROQ_API_KEY="your_groq_api_key_here"

# Windows
setx GROQ_API_KEY "your_groq_api_key_here"
```

---

## Running the API

Start the FastAPI server locally:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

---

## API Usage Examples (cURL & Postman)

### 1. Upload Leads CSV

**cURL (Local):**
```bash
curl -X POST "http://localhost:8001/leads/upload" -F "file=@leads_30.csv"
```

**cURL (Production):**
```bash
curl -X POST "https://fast-api-ideal-service-extractor.onrender.com/leads/upload" -F "file=@leads_30.csv"
```

**Postman:**
- Method: POST
- URL: `http://localhost:8001/leads/upload`
- Body: form-data, key: `file`, value: select CSV file

### 2. Create Offer & Score Leads

**cURL (Local):**
```bash
curl -X POST "http://localhost:8001/offer" \
-H "Content-Type: application/json" \
-d '{"name":"AI Outreach Automation","value_props":["24/7 outreach","6x more meetings"],"ideal_use_cases":["B2B SaaS mid-market"]}'
```

**cURL (Production):**
```bash
curl -X POST "https://fast-api-ideal-service-extractor.onrender.com/offer" \
-H "Content-Type: application/json" \
-d "{\"name\":\"AI Outreach Automation\",\"value_props\":[\"24/7 outreach\",\"6x more meetings\"],\"ideal_use_cases\":[\"B2B SaaS mid-market\"]}"
```

**Postman:**
- Method: POST
- URL: `http://localhost:8001/offer`
- Headers: `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"]
}
```

### 3. Download Scored CSV Results

**cURL (Local):**
```bash
curl -f -o my_leads.csv http://localhost:8001/download-csv
```

**cURL (Production):**
```bash
curl -f -o my_leads.csv https://fast-api-ideal-service-extractor.onrender.com/download-csv
```

**Postman:**
- Method: GET
- URL: `http://localhost:8001/download-csv`
- Send & Save Response → Save to file

---

## Rule Logic & AI Prompt Explanation

### Rule-based scoring:

1. **Role Relevance**
   * Decision-makers (CEO, VP Sales, Head of Growth, etc.) → +20 points
   * Influencers (Marketing Manager, Product Manager, etc.) → +10 points

2. **Industry Match**
   * Exact match with `offer.ideal_use_cases` → +20 points
   * Adjacent industries (FinTech, AI SaaS, Consulting, Software, Cloud, Technology) → +10 points

3. **Data Completeness**
   * All lead fields filled → +10 points

### AI Prompt Structure & Logic:

The system sends a structured prompt to the Groq LLaMA model containing:
- **Offer Information**: Value propositions and ideal use cases
- **Lead Data**: Name, role, company, industry, location, bio
- **Role Classification**: Decision/Influencer type from rule-based logic

**Sample Input to AI Model:**
```
Classify this lead's intent and provide concise reasoning.

Value Props: ["24/7 outreach", "6x more meetings"]
Ideal Use Cases: ["B2B SaaS mid-market"]

Lead: Ava Patel, Head of Growth, FlowMetrics, SaaS, San Francisco, "Helping B2B SaaS companies accelerate pipeline growth..."
Role Type: decision

Respond in exactly this format:
"intent": "High"
"reasoning": "Brief reason here"
```

**Expected AI Response:**
```json
"intent": "High"
"reasoning": "Fits ideal use case of B2B SaaS mid-market and has a decision-making role"
```

The AI analyzes the lead's profile against the offer's value propositions and ideal use cases to determine intent level and provide reasoning.