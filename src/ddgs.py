import sys
import time
from duckduckgo_search import DDGS

def search_ddg(queries: list[str]) -> list[dict]:
    # perform searches on ddg and get unique results back
    t = time.time()
    seen = set()
    results = []
    for i, q in enumerate(queries):
        if i > 0:
            # added sum delay between searches to stop the ratelimit issues 🌿
            time.sleep(1.5)
        try:
            with DDGS() as ddgs:
                hits = list(ddgs.text(q, max_results=5))
        except Exception as e:
            print(f"🌿 search errror: {e}", file=sys.stderr)
            continue
        for h in hits:
            url = h.get("href", h.get("link", ""))
            if url and url not in seen:
                seen.add(url)
                results.append({
                    "title": h.get("title", ""),
                    "url": url,
                    "snippet": h.get("body", h.get("snippet", "")),
                })
    elapsed = round(time.time() - t, 2)
    # returning results without print so engine can use a nice spinner success line
    return results, elapsed
