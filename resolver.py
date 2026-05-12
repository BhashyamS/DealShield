import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote_plus, parse_qs, unquote


def is_url(user_input):
    return "." in user_input or user_input.startswith(("http://", "https://"))


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def clean_duckduckgo_url(href):
    """
    DuckDuckGo often returns redirect links like:
    //duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.doordash.com%2F...

    This function extracts the real website from the uddg parameter.
    """
    if not href:
        return None

    if href.startswith("//"):
        href = "https:" + href

    parsed = urlparse(href)

    if "duckduckgo.com" in parsed.netloc and "/l/" in parsed.path:
        query_params = parse_qs(parsed.query)
        if "uddg" in query_params:
            return unquote(query_params["uddg"][0])

    return href


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
    seen_urls = set()

    for result in soup.select(".result"):
        link = result.select_one(".result__a")

        if not link:
            continue

        title = link.get_text(" ", strip=True)
        raw_href = link.get("href")
        cleaned_url = clean_duckduckgo_url(raw_href)

        if not cleaned_url:
            continue

        parsed = urlparse(cleaned_url)

        if not parsed.netloc:
            continue

        if cleaned_url in seen_urls:
            continue

        seen_urls.add(cleaned_url)

        results.append({
            "title": title,
            "url": cleaned_url,
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
