import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


LEGAL_KEYWORDS = {
    "terms": [
        "terms",
        "terms of service",
        "terms and conditions",
        "user agreement"
    ],
    "privacy": [
        "privacy",
        "privacy policy"
    ],
    "refund": [
        "refund",
        "returns",
        "return policy"
    ],
    "cancellation": [
        "cancel",
        "cancellation",
        "terminate",
        "termination"
    ],
    "subscription": [
        "subscription",
        "membership",
        "billing",
        "auto-renewal",
        "renewal"
    ],
}


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def get_page_html(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    return response.text


def find_legal_links(base_url):
    base_url = normalize_url(base_url)

    try:
        html = get_page_html(base_url)
    except Exception as e:
        return {
            "error": f"Could not access website: {e}",
            "links": []
        }

    soup = BeautifulSoup(html, "html.parser")

    links_found = []

    for a_tag in soup.find_all("a", href=True):
        link_text = a_tag.get_text(" ", strip=True).lower()
        href = a_tag["href"].lower()

        full_url = urljoin(base_url, a_tag["href"])

        combined_text = f"{link_text} {href}"

        for category, keywords in LEGAL_KEYWORDS.items():
            if any(keyword in combined_text for keyword in keywords):
                links_found.append({
                    "category": category,
                    "text": a_tag.get_text(" ", strip=True),
                    "url": full_url
                })

    unique_links = []
    seen_urls = set()

    for link in links_found:
        if link["url"] not in seen_urls:
            unique_links.append(link)
            seen_urls.add(link["url"])

    return {
        "error": None,
        "links": unique_links
    }
