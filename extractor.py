import re
import requests
from bs4 import BeautifulSoup


MAX_PAGES_TO_EXTRACT = 10
MAX_CHARS_PER_PAGE = 8000


def get_headers():
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\xa0", " ")
    return text.strip()


def extract_text_from_url(url):
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = clean_text(text)

    return {
        "success": True,
        "text": text[:MAX_CHARS_PER_PAGE],
        "error": None
    }


def prioritize_links(links):
    priority = {
        "terms": 1,
        "subscription": 2,
        "cancellation": 3,
        "refund": 4,
        "privacy": 5,
        "policy": 6
    }

    return sorted(
        links,
        key=lambda x: priority.get(x.get("category", "policy"), 99)
    )


def extract_policy_bundle(links):
    selected_links = prioritize_links(links)[:MAX_PAGES_TO_EXTRACT]
    bundle = []

    for link in selected_links:
        extracted = extract_text_from_url(link["url"])

        text = extracted["text"]
        if not text:
            text = link.get("snippet", "")

        bundle.append({
            "category": link.get("category", "policy"),
            "title": link.get("title", ""),
            "url": link.get("url", ""),
            "source": link.get("source", ""),
            "snippet": link.get("snippet", ""),
            "extracted_text": text,
            "extraction_success": extracted["success"],
            "extraction_error": extracted["error"]
        })

    return bundle
