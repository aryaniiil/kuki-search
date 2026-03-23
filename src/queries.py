import json
import time
import os
from litellm import completion

def generate_search_queries(user_query: str, model: str, api_key: str = None, base_url: str = None) -> list[str]:
    # generate search queries for the prompt using an llm
    t = time.time()
    
    # read prompt from .md file
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "subqueries.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        subqueries_prompt = f.read()

    # config setup
    completion_kwargs = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": 200,
        "messages": [
            {
                "role": "system",
                "content": subqueries_prompt,
            },
            {"role": "user", "content": user_query},
        ]
    }
    
    # add optional creds if they are there
    if api_key:
        completion_kwargs["api_key"] = api_key
    if base_url:
        completion_kwargs["base_url"] = base_url

    try:
        response = completion(**completion_kwargs)
        raw = response.choices[0].message.content.strip()
        
        # clean markdown json garbage
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()
        
        queries = json.loads(raw)[:5]
        elapsed = round(time.time() - t, 2)
        
        # we let the engine print the main success but we keep the list for logging
        print("")
        for i, q in enumerate(queries, 1):
             print(f"   🌿 {i}. {q}")
            
        return queries, elapsed

    except Exception as e:
        print(f"🌿 error generating queries: {e}")
        return [user_query], 0.0
