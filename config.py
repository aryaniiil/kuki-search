import os
from litellm import completion

# llm config things
# we use litellm bc it suports evrything (openai anthropic etc)
# use anthropic/name or any other recognised provider else use baseurl
LLM_MODEL = os.environ.get("LLM_MODEL", "modelname") 
LLM_API_KEY = os.environ.get("LLM_API_KEY", "modelapi")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "baseurl")

# litellm uses these if they in env
# can also pass them into complete call
