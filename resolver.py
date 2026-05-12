import re
import requests
from urllib.parse import urlparse, urlunparse


BLOCKED_DOMAINS = [
    "wikipedia.org",
    "instagram.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "tiktok.com",
    "play.google.com",
    "apps.apple.com",
    "apps.microsoft.com",
    "reddit.com",
    "pinterest.com",
]


def is_url(user_input):
    return "." in user_input or user_input.startswith(("http://", "https://"))


def clean_url(url):
    parsed = urlparse(url)

    clean = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.rstrip("/") or "",
        "",
        "",
        ""
    ))

    return clean


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return clean_url(url)


def get_domain(url):
    parsed = urlparse(normalize_url(url))
    return parsed.netloc.replace("www.", "")


def normalize_company_name(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def is_blocked_domain(url):
    domain = get_domain(url)
    return any(blocked in domain for blocked in BLOCKED_DOMAINS)


def is_likely_official(company_name, url, title=""):
    company_key = normalize_company_name(company_name)
    domain_key = normalize_company_name(get_domain(url))
    title_key = normalize_company_name(title)

    if not company_key:
        return False

    return company_key in domain_key or company_key in title_key


def result_score(company_name, item):
    url = clean_url(item.get("url", ""))
    title = item.get("title", "")
    content = item.get("content", "")

    score = 0

    if is_blocked_domain(url):
        score -= 100

    if is_likely_official(company_name, url, title):
        score += 60

    domain = get_domain(url)
    path = urlparse(url).path.lower()

    if path in ["", "/"]:
        score += 25

    if any(word in title.lower() for word in ["official", "home", company_name.lower()]):
        score += 15

    if any(word in (title + " " + content).lower() for word in ["official website", "homepage"]):
        score += 10

    if any(bad in path for bad in ["/wiki", "/store/apps", "/login", "/contact", "/support"]):
        score -= 25

    if domain.startswith("help.") or "support" in domain:
        score -= 10

    return score


def search_company_name(company_name, tavily_api_key):
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": tavily_api_key,
        "query": f"{company_name} official website homepage",
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 10
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
    except Exception as e:
        return {
            "error": f"Tavily API error: {e}",
            "results": []
        }

    data = response.json()
    candidates = []
    seen_urls = set()

    for item in data.get("results", []):
        raw_url = item.get("url", "")
        if not raw_url:
            continue

        cleaned = clean_url(raw_url)
        if cleaned in seen_urls:
            continue

        seen_urls.add(cleaned)

        candidate = {
            "title": item.get("title", "Unknown"),
            "url": cleaned,
            "content": item.get("content", "")
        }
        candidate["_score"] = result_score(company_name, candidate)
        candidates.append(candidate)

    # Add a direct official-domain guess. This helps when search returns social/app-store pages first.
    guessed_url = f"https://www.{normalize_company_name(company_name)}.com"
    if guessed_url not in seen_urls:
        guessed = {
            "title": f"{company_name.title()} Official Website",
            "url": guessed_url,
            "content": "Direct official website guess based on company name.",
            "_score": 55
        }
        candidates.append(guessed)

    candidates = sorted(candidates, key=lambda x: x["_score"], reverse=True)

    filtered = []
    for candidate in candidates:
        if candidate["_score"] < -20:
            continue
        candidate.pop("_score", None)
        filtered.append(candidate)

    return {
        "error": None,
        "results": filtered[:5]
    }


def resolve_company_input(user_input, tavily_api_key):
    user_input = user_input.strip()

    if is_url(user_input):
        return {
            "type": "url",
            "url": normalize_url(user_input),
            "options": [],
            "error": None
        }

    search_result = search_company_name(user_input, tavily_api_key)

    if search_result["error"]:
        return {
            "type": "search",
            "url": None,
            "options": [],
            "error": search_result["error"]
        }

    return {
        "type": "search",
        "url": None,
        "options": search_result["results"],
        "error": None
    }
