# FinePrint AI v6

## Features

- Company name OR URL input
- Secure Tavily API key through Streamlit Secrets
- Cleans tracking URLs like `?rsltid=...`
- Tries homepage scraping first
- If homepage scraping is blocked, uses Tavily fallback search
- Finds:
  - Terms of Service
  - Privacy Policy
  - Refund Policy
  - Cancellation Policy
  - Subscription/Billing pages

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
TAVILY_API_KEY = "your_real_api_key_here"
```

Run:

```bash
streamlit run app.py
```

## Streamlit Cloud Setup

In Streamlit Cloud, add this to App Settings → Secrets:

```toml
TAVILY_API_KEY = "your_real_api_key_here"
```
