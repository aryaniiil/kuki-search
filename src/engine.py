import asyncio
import os
import json
import re
import time
from datetime import datetime
from litellm import completion
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from halo import Halo

from src.ddgs import search_ddg
from src.tavily_search import search_tavily
from src.queries import generate_search_queries
import config as app_config

class SearchEngine:
    def __init__(self, model: str, api_key: str = None, base_url: str = None, tavily_api_key: str = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.tavily_api_key = tavily_api_key
        self.output_dir = "Results" # base root dir
        self.crawler_initialized = False

    @staticmethod
    def _strip_links(text: str) -> str:
        # cleaning markdown links and urls away
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'^\s*\[\d+\]:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    @staticmethod
    def _clean_text(text: str, max_chars: int = 1200) -> str:
        # crop to max chars near the end of a sentence
        text = SearchEngine._strip_links(text)
        if len(text) <= max_chars:
            return text
        truncated = text[:max_chars]
        last_period = truncated.rfind('.')
        if last_period > max_chars * 0.5:
            return truncated[:last_period + 1]
        return truncated + "..."

    def _save_json(self, folder: str, filename: str, data: dict):
        # putting a dict into a json file in the specific query folder
        path = os.path.join(self.output_dir, folder)
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def _crawl_single(self, crawler, config, item: dict, index: int) -> dict:
        # crawl just one single url and get clean markdown back
        try:
            result = await crawler.arun(url=item["url"], config=config)
            if result.success and result.markdown:
                raw_content = result.markdown.markdown_with_citations or ""
                content = self._clean_text(raw_content)
            else:
                content = self._clean_text(item.get("snippet", ""))
        except Exception:
            content = self._clean_text(item.get("snippet", ""))

        return {
            "index": index,
            "title": item["title"],
            "url": item["url"],
            "content": content,
        }

    async def crawl_pages(self, results: list[dict], query_folder: str, top_n: int = 10) -> list[dict]:
        # crawl the top n results concurrently
        t = time.time()
        to_crawl = results[:top_n]

        md_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.45),
            options={"citations": False, "ignore_links": True, "ignore_images": True, "body_width": 0},
        )
        config = CrawlerRunConfig(
            markdown_generator=md_generator,
            excluded_tags=["nav", "footer", "header", "aside", "form"],
            cache_mode="bypass",
        )

        async with AsyncWebCrawler() as crawler:
            tasks = [self._crawl_single(crawler, config, item, i + 1) for i, item in enumerate(to_crawl)]
            enriched = await asyncio.gather(*tasks)

        enriched = sorted(enriched, key=lambda x: x["index"])
        enriched = [e for e in enriched if e["content"]]
        elapsed = round(time.time() - t, 2)
        
        # log what we found
        self._save_json(query_folder, "3_crawled_data.json", {
            "total_crawled": len(enriched),
            "time_seconds": elapsed,
            "sources": enriched,
        })
        print(f"🌿 crawled {len(enriched)} pages together ({elapsed}s)")
        return enriched

    @staticmethod
    def build_context(enriched: list[dict]) -> str:
        # build the string context for our research synthesis
        parts = []
        for item in enriched:
            parts.append(f"[{item['index']}] {item['title']}\nURL: {item['url']}\n{item['content']}\n")
        return "\n---\n".join(parts)

    def stream_verdict(self, user_query: str, context: str, query_folder: str):
        # find the research prompt in prompts/ folder
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "research.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            research_prompt = f.read()

        # injecting current date so its not hallucinating based on training data
        current_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        completion_kwargs = {
            "model": self.model,
            "temperature": 0.3,
            "stream": True,
            "messages": [
                {"role": "system", "content": f"{research_prompt}\n\nCURRENT DATE/TIME: {current_date_str}"},
                {"role": "user", "content": f"QUERY: {user_query}\n\nSOURCES:\n{context}"},
            ]
        }
        
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key
        if self.base_url:
            completion_kwargs["base_url"] = self.base_url

        try:
            stream = completion(**completion_kwargs)
            
            full_response = []
            print("\n🌿 " + "=" * 57)
            print("🌿 ANSWER")
            print("🌿 " + "=" * 57 + "\n")

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    print(delta.content, end="", flush=True)
                    full_response.append(delta.content)

            print("\n")
            verdict = "".join(full_response)

            self._save_json(query_folder, "final_answer.json", {
                "query": user_query,
                "answer": verdict,
                "timestamp": datetime.now().isoformat(),
            })
            return verdict
        except Exception as e:
            # warn if the stream fails for sum reason
            print(f"🌿 error streaming verdict: {e}")
            return "failed to generate answer."

    async def run(self, user_query: str, query_folder: str):
        # engine starting point
        total_start = time.time()
        print(f"\n🌿 query: {user_query}\n")

        # 1. generate subqueries
        # fix: queriess -> queries and added a newline print after success
        spinner = Halo(text='🌿 thinking of queries...', spinner='dots', color='green')
        spinner.start()
        queries, q_elapsed = generate_search_queries(user_query, self.model, self.api_key, self.base_url)
        spinner.succeed(f"🌿 queries generated ({q_elapsed}s)")
        print("") # fix: needed space after thinking of queries 🌿

        self._save_json(query_folder, "1_queries.json", {
            "user_query": user_query, 
            "generated_queries": queries, 
            "time_seconds": q_elapsed
        })

        # 2. search with configured provider
        spinner = Halo(text='🌿 searching the webs...', spinner='dots', color='green')
        spinner.start()
        if app_config.SEARCH_PROVIDER == "tavily":
            raw_results, s_elapsed = search_tavily(queries, api_key=self.tavily_api_key)
        else:
            raw_results, s_elapsed = search_ddg(queries)
        spinner.succeed(f"🌿 found {len(raw_results)} unique results ({s_elapsed}s)\n")

        self._save_json(query_folder, "2_search_results.json", {
            "total_results": len(raw_results), 
            "time_seconds": s_elapsed, 
            "results": raw_results
        })

        # 3. concurrent crawl
        enriched = await self.crawl_pages(raw_results, query_folder, top_n=10)
        
        if not enriched:
            print("🌿 no contents found.")
            return

        # 4. synthesis
        context = self.build_context(enriched)
        total_prep = round(time.time() - total_start, 2)
        print(f"\n🌿 total prep time: {total_prep}s")

        self.stream_verdict(user_query, context, query_folder)
        print(f"🌿 results saved into ./{self.output_dir}/{query_folder}/")