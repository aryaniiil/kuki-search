import asyncio
import os
import sys
import re
from src.engine import SearchEngine
import config

def get_output_dir(query: str, max_len: int = 40) -> str:
    # cleaning the query for folder naming and cutting if its to long
    clean_q = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip().replace(" ", "_").lower()
    if len(clean_q) > max_len:
        clean_q = clean_q[:max_len].strip("_")
    return clean_q or "search_results"

async def run_main():
    if len(sys.argv) < 2:
        print("🌿 usage: python main.py \"your query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # init the engine here
    engine = SearchEngine(
        model=config.LLM_MODEL,
        api_key=config.LLM_API_KEY,
        base_url=config.LLM_BASE_URL
    )

    # query processing
    query_folder = get_output_dir(query)
    
    # run the main search engine
    await engine.run(query, query_folder)

def main():
    try:
        asyncio.run(run_main())
    except KeyboardInterrupt:
        print("\n🌿 research aborted by useer.")
        sys.exit(0)

if __name__ == "__main__":
    main()