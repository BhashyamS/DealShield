# FinePrint AI v7

FinePrint AI helps users understand the hidden catch before they click agree.

## Features

- Company name OR URL input
- Tavily-powered company discovery
- URL cleaning
- Homepage scraping + Tavily fallback search
- Policy page discovery
- Policy text extraction
- Gemini-powered consumer risk report
- Red flag detection for:
  - recurring billing
  - auto-renewal
  - cancellation deadlines
  - refund restrictions
  - hidden subscription risks

## Local Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create:

```text
.streamlit/secrets.toml
```

Add:

```toml
TAVILY_API_KEY = "your_tavily_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
```

Run:

```bash
streamlit run app.py
```

## Streamlit Cloud Setup

In Streamlit Cloud, add this to App Settings → Secrets:

```toml
TAVILY_API_KEY = "your_tavily_key_here"
GEMINI_API_KEY = "your_gemini_key_here"
```

## Note

This app is not legal advice. It summarizes publicly available policy text and flags consumer-risk patterns.
