import requests

from resolver import clean_url, get_domain
from scraper import find_legal_links, categorize_text


POLICY_SEARCHES = [
    ("terms", "terms of service OR terms and conditions OR user agreement"),
    ("subscription", "membership pricing OR subscription terms OR billing OR auto renewal OR membership agreement OR fees"),
    ("cancellation", "cancellation policy OR cancel membership OR terminate subscription OR early termination fee"),
    ("refund", "refund policy OR return policy OR non refundable"),
    ("privacy", "privacy policy"),
]


def tavily_search(query, tavily_api_key, max_results=5):
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": tavily_api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": max_results
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json().get("results", [])


def find_policy_pages_with_tavily(company_name, website_url, tavily_api_key):
    domain = get_domain(website_url)
    all_links = []
    seen_urls = set()

    for fallback_category, search_phrase in POLICY_SEARCHES:
        query = f"site:{domain} {search_phrase}"

        try:
            results = tavily_search(query, tavily_api_key, max_results=5)
        except Exception:
            results = []

        for item in results:
            raw_url = item.get("url", "")
            if not raw_url:
                continue

            cleaned = clean_url(raw_url)

            if domain not in cleaned:
                continue

            if cleaned in seen_urls:
                continue

            title = item.get("title", fallback_category.title())
            snippet = item.get("content", "")
            category = categorize_text(f"{title} {cleaned} {snippet}")

            if category == "policy":
                category = fallback_category

            seen_urls.add(cleaned)

            all_links.append({
                "category": category,
                "title": title,
                "url": cleaned,
                "source": "tavily fallback",
                "snippet": snippet
            })

    return all_links


def dedupe_links(links):
    deduped = []
    seen = set()

    for link in links:
        url = clean_url(link["url"])
        if url in seen:
            continue

        seen.add(url)
        link["url"] = url
        deduped.append(link)

    return deduped


def scan_for_policy_pages(company_name, website_url, tavily_api_key):
    cleaned_url = clean_url(website_url)

    homepage_result = find_legal_links(cleaned_url)
    homepage_links = homepage_result.get("links", [])
    homepage_error = homepage_result.get("error")

    fallback_links = []

    if homepage_error or len(homepage_links) < 2:
        fallback_links = find_policy_pages_with_tavily(
            company_name=company_name,
            website_url=cleaned_url,
            tavily_api_key=tavily_api_key
        )

    all_links = dedupe_links(homepage_links + fallback_links)

    return {
        "cleaned_url": cleaned_url,
        "homepage_error": homepage_error,
        "links": all_links
    }
