# FinePrint AI v8

## Improvements in v8

- Better official website selection
- Filters out Wikipedia, Instagram, Google Play, app stores, social media, and support/login pages
- Adds a direct official-domain guess such as `https://www.doordash.com`
- Adds AI-generated membership/subscription table
- Adds AI-generated all-fees table
- Stronger focus on cancellation fees, join fees, monthly fees, annual fees, trials, auto-renewal, and vague fee language

## Local Setup

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
