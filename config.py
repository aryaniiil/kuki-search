import os
import sys

# llm config things
# we use litellm bc it supports everything (openai, anthropic, etc.)
LLM_MODEL = os.environ.get("LLM_MODEL", "modelname") 
LLM_API_KEY = os.environ.get("LLM_API_KEY", "modelapi")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "baseurl")

# search provider config
# set SEARCH_PROVIDER to 'tavily' to use Tavily, default is 'ddg' (DuckDuckGo)
SEARCH_PROVIDER = os.environ.get("SEARCH_PROVIDER", "ddg").lower()
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Early validation for Tavily
if SEARCH_PROVIDER == "tavily" and not TAVILY_API_KEY:
    print("🌿 Critical Error: SEARCH_PROVIDER is set to 'tavily' but TAVILY_API_KEY is missing.", file=sys.stderr)
    print("🌿 Please set TAVILY_API_KEY in your environment or change SEARCH_PROVIDER to 'ddg'.", file=sys.stderr)
    sys.exit(1)
