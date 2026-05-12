import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus


def is_url(user_input):
    return "." in user_input or user_input.startswith(("http://", "https://"))


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def search_company_name(company_name):
    query = quote_plus(company_name + " official website")
    search_url = f"https://duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return {
            "error": f"Could not search company name: {e}",
            "results": []
        }

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".result"):
        link = result.select_one(".result__a")

        if not link:
            continue

        title = link.get_text(" ", strip=True)
        href = link.get("href")

        if not href:
            continue

        parsed = urlparse(href)

        results.append({
            "title": title,
            "url": href,
            "domain": parsed.netloc
        })

        if len(results) >= 5:
            break

    return {
        "error": None,
        "results": results
    }


def resolve_company_input(user_input):
    user_input = user_input.strip()

    if is_url(user_input):
        return {
            "type": "url",
            "url": normalize_url(user_input),
            "options": [],
            "error": None
        }

    search_result = search_company_name(user_input)

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
