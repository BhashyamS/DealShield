import json
import re
import requests


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def build_analysis_text(policy_bundle):
    sections = []

    for item in policy_bundle:
        text = item.get("extracted_text") or item.get("snippet") or ""
        if not text:
            continue

        section = f"""
SOURCE TITLE: {item.get("title")}
CATEGORY: {item.get("category")}
URL: {item.get("url")}
TEXT:
{text}
"""
        sections.append(section)

    return "\n\n---\n\n".join(sections)


def extract_json(text):
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in Gemini response.")

    return json.loads(match.group(0))


def call_gemini(prompt, gemini_api_key, model=DEFAULT_GEMINI_MODEL):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": gemini_api_key
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "responseMimeType": "application/json"
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


def analyze_consumer_risk(company_name, website_url, policy_bundle, gemini_api_key):
    analysis_text = build_analysis_text(policy_bundle)

    if not analysis_text:
        return {
            "error": "No policy text was available to analyze.",
            "raw_text": ""
        }

    prompt = f"""
You are FinePrint AI, a consumer protection assistant.

Analyze the following public policy text and search snippets for consumer risk.

Company: {company_name}
Website: {website_url}

Focus especially on:
- membership options
- subscription tiers
- plan names
- free trials
- recurring billing
- all fees, including monthly fees, annual fees, join fees, service fees, taxes, cancellation fees, early termination fees, refund fees, processing fees, delivery fees, or any vague fee language
- cancellation deadlines
- refund restrictions
- auto-renewal
- forced arbitration
- class action waiver

Important:
- Do NOT make up numbers.
- If a fee amount is not stated, write "Not specified".
- If membership options are unclear, still list whatever options are mentioned and mark unknown fields as "Not specified".
- Do NOT provide legal advice.
- Only make claims supported by the provided text/snippets.
- If evidence is weak or from snippets only, say so.

Return ONLY valid JSON with this exact structure:

{{
  "risk_score": 0,
  "risk_level": "Low | Moderate | High",
  "summary": "plain English summary",
  "membership_options": [
    {{
      "plan_or_membership": "name of plan/membership",
      "price": "amount or Not specified",
      "billing_frequency": "monthly/annual/weekly/etc or Not specified",
      "trial_terms": "trial details or Not specified",
      "auto_renewal": "Yes/No/Not specified",
      "cancellation_terms": "plain English cancellation terms",
      "fees_or_penalties": "fees tied to this plan"
    }}
  ],
  "all_fees": [
    {{
      "fee_type": "monthly fee/annual fee/join fee/cancellation fee/etc",
      "amount": "amount or Not specified",
      "when_charged": "when this fee applies",
      "source_context": "short supporting quote or paraphrase from provided text"
    }}
  ],
  "red_flags": ["red flag 1", "red flag 2"],
  "billing_findings": ["finding 1", "finding 2"],
  "cancellation_refund_findings": ["finding 1", "finding 2"],
  "positive_signs": ["positive sign 1", "positive sign 2"],
  "recommended_action": "what the user should do before signing up",
  "evidence_limitations": "what information was missing or unclear"
}}

Scoring guide:
0-30 = Low risk
31-65 = Moderate risk
66-100 = High risk

Policy text:
{analysis_text[:50000]}
"""

    try:
        raw_text = call_gemini(prompt, gemini_api_key)
        report = extract_json(raw_text)
        return report
    except Exception as e:
        return {
            "error": f"Gemini analysis failed: {e}",
            "raw_text": locals().get("raw_text", "")
        }
