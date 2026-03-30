import time
import sys
from tavily import TavilyClient

def search_tavily(queries: list[str], api_key: str = None) -> tuple[list[dict], float]:
    if not api_key or not api_key.strip():
        print("🌿 Error: Tavily API key is missing or empty.", file=sys.stderr)
        return [], 0.0

    t = time.time()
    try:
        client = TavilyClient(api_key=api_key)
    except Exception as e:
        print(f"🌿 Error initializing Tavily client: {e}", file=sys.stderr)
        return [], 0.0

    seen = set()
    results = []

    for q in queries:
        try:
            response = client.search(query=q, max_results=5)
            for hit in response.get("results", []):
                url = hit.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    results.append({
                        "title": hit.get("title", ""),
                        "url": url,
                        "snippet": hit.get("content", ""),
                    })
        except Exception as e:
            print(f"🌿 Tavily search error for query '{q}': {e}", file=sys.stderr)
            continue

    elapsed = round(time.time() - t, 2)
    return results, elapsed
