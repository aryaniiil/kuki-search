# 🌿 kuki research

kuki search is a fast and concurent reserch engine for deep web analysis and synthesis. it uses duckduckgo for broad search and crawl4ai for markdown content. 🌿

## 🌿 features

- 🌿 **concurent crawling:** fast fetching and parsing of multiple results using `crawl4ai`
- 🌿 **smart synthesis:** auto-generates subqueries to make sure everythng is covered 🌿
- 🌿 **universal llm support:** built on `litellm` so it works with openai, anthropic, gemini, kimi and more
- 🌿 **clean resuts:** saves summarized insights 🌿
- 🌿 **perfomance optimized:** kinda fast

## 🌿 project structure

```text
├── config.py           # llm config and things 🌿
├── main.py             # entry point and crawler warmup 🌿
├── src/
│   ├── engine.py       # core logic and research pipeline 🌿
│   ├── ddgs.py         # duckduckgo search stuff 🌿
│   ├── queries.py      # llm sub-query logic 🌿
│   └── prompts/        # prompt stings for research 🌿
│       ├── subqueries.md
│       └── research.md
└── results/        # logs and results 🌿
```

## 🌿 setup

1. 🌿 **instalation:**
   get the dependencies ready:
   ```bash
   python -m pip install requirements.txt
   ```

2. 🌿 **configuation:**
   change `config.py` or set env vars for ur llm.
   ```python
   LLM_MODEL = "gpt-4"
   LLM_API_KEY = "your-api-key"
   ```

## 🌿 usage

just run it with ur query as an argument:

```bash
python main.py "How do the current battery technologies compare for EV range?"
```

🌿 the engine will:
1. 🌿 initialize and pre-warm the cralwer 🌿
2. 🌿 generate 5 subqueries 🌿
3. 🌿 search and crawl top 10 results at once 🌿
4. 🌿 synthesize final answer with citations 🌿
5. 🌿 save it all in a folder named after ur query 🌿

## 🌿 architecture

its a fairly simple project, and will implement more features in the future! 🌿
