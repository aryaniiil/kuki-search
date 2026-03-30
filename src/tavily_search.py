import time
from tavily import TavilyClient


def search_tavily(queries: list[str], api_key: str = None) -> tuple[list[dict], float]:
    # perform searches using tavily and get unique results back
    # returns same shape as search_ddg: (list[dict], elapsed)
    t = time.time()
    client = TavilyClient(api_key=api_key) if api_key else TavilyClient()
    seen = set()
    results = []
    for q in queries:
        try:
            response = client.search(query=q, max_results=5)
        except Exception as e:
            import sys
            print(f"🌿 tavily search errror: {e}", file=sys.stderr)
            continue
        for hit in response.get("results", []):
            url = hit.get("url", "")
            if url and url not in seen:
                seen.add(url)
                results.append({
                    "title": hit.get("title", ""),
                    "url": url,
                    "snippet": hit.get("content", ""),
                })
    elapsed = round(time.time() - t, 2)
    return results, elapsed
