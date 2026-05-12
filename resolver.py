import requests


def is_url(user_input):
    return "." in user_input or user_input.startswith(("http://", "https://"))


def normalize_url(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def search_company_name(company_name, tavily_api_key):
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": tavily_api_key,
        "query": f"{company_name} official website",
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 5
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

    results = []

    for item in data.get("results", []):
        results.append({
            "title": item.get("title", "Unknown"),
            "url": item.get("url", ""),
            "content": item.get("content", "")
        })

    return {
        "error": None,
        "results": results
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

    search_result = search_company_name(
        user_input,
        tavily_api_key
    )

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
