# app/core/search.py
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import wikipedia
import hashlib
import time
from urllib.parse import quote, urlparse
import random
from .twitter import TwitterFetcher
from ..config import get_settings
from ..utils.logging import get_logger
import os

settings = get_settings()
logger = get_logger("fact_checker.core.search")

class MultiSearchTool:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) Firefox/89.0'
        ]
        self.twitter_fetcher = TwitterFetcher(settings.TWITTER_BEARER_TOKEN)
        logger.info("MultiSearchTool initialized")

    def get_tweet_data(self, tweet_id: str) -> Optional[Dict]:
        try:
            logger.info(f"Fetching tweet data for ID: {tweet_id}")
            return self.twitter_fetcher.get_tweets(tweet_id)
        except Exception as e:
            logger.error(f"Error fetching tweet {tweet_id}: {str(e)}")
            return None

    def _get_google_results(self, query: str) -> List[Dict]:
        try:
            logger.info(f"Performing Google search for: {query}")
            headers = {'User-Agent': random.choice(self.user_agents)}
            num_results = 1
            encoded_query = quote(query)
            # """Tool to search via Google CSE"""
            api_key = os.getenv("GOOGLE_API_KEY", "")
            cx = os.getenv("GOOGLE_CSE_ID", "")
            base_url = "https://www.googleapis.com/customsearch/v1"
            url = f"{base_url}?key={api_key}&cx={cx}&q={encoded_query}&num={num_results}"
            response = requests.get(url, timeout=15)
            data = response.json()
            # logger.info(f"MY RESPONSEEEE!!!, {data}")
            # logger.info(f"RESPONSE!  {response.text[:500]}")
            if response.status_code != 200:
                logger.info(f"Google search failed with status code: {response.status_code}")
                return []
            
            results = []
            
            if "items" in data:
                for item in data["items"]:
                    logger.info('Found Google result: ( title: "%s", snippet: "%s" )', item.get("title"), item.get("snippet"))

                    found_res = {
                        "title": item["title"],
                        "snippet": item["snippet"],
                        "url": item["link"],
                        "domain": urlparse(item["link"]).netloc,
                        "engine": "google"
                    }
                    results.append(found_res)
                    # logger.info(f"DOMAIN HERE IS: {urlparse(item['link']).netloc}")
                    # logger.info(F"I AM PUSHING {found_res} TO RESULTS!!!")
                # logger.info("I am totally in ITEMS!!!")
            else:
                logger.info("I am totally out of ITEMS!!!")
                
            logger.info(f"Found {len(results)} Google results")
            return results[:5]

        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return []

    def _get_ddg_results(self, query: str) -> List[Dict]:
        try:
            # logger.info(f"Performing DuckDuckGo search for: {query}")
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=5):
                    logger.info('Found DuckDuckGo result: [ title: "%s", snippet: "%s" ]', r.get("title"), r.get("body"))
                    results.append({
                        "title": r['title'],
                        "snippet": r['body'],
                        "url": r.get('href', 'No URL available'),
                        "domain": urlparse(r.get('href', '')).netloc,
                        "engine": "duckduckgo"
                    })
                    logger.debug(f"Found DuckDuckGo result: {r.get('href', 'No URL available')}")
                
                logger.info(f"Found {len(results)} DuckDuckGo results")
                return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []

    def _get_wiki_results(self, query: str) -> List[Dict]:
        try:
            logger.debug(f"Performing Wikipedia search for: {query}")
            search_results = wikipedia.search(query, results=3)
            results = []

            for title in search_results:
                try:
                    page = wikipedia.page(title, auto_suggest=False)
                    summary = page.summary
                    if len(summary) > 300:
                        summary = summary[:300] + "..."
                    logger.info('Found Wikipedia result: { title: "%s", snippet: "%s" }', page.title, summary)

                    results.append({
                        "title": page.title,
                        "snippet": summary,
                        "url": page.url,
                        "domain": "wikipedia.org",
                        "engine": "wikipedia"
                    })
                    logger.debug(f"Found Wikipedia result: {page.title}")
                except Exception as e:
                    logger.warning(f"Error processing Wikipedia page {title}: {str(e)}")
                    continue

            logger.info(f"Found {len(results)} Wikipedia results")
            return results

        except Exception as e:
            logger.error(f"Wikipedia search error: {str(e)}")
            return []

    def get_additional_context(self, query: str, tweet_data: Optional[Dict] = None) -> Dict:
        logger.info("Getting additional context")
        context = {}

        try:
            wiki_results = self._get_wiki_results(query)
            if wiki_results:
                context["wikipedia"] = {
                    "summary": wiki_results[0]["snippet"],
                    "url": wiki_results[0]["url"]
                }
                logger.debug("Added Wikipedia context")
        except Exception as e:
            logger.warning(f"Error getting Wikipedia context: {str(e)}")

        if tweet_data:
            try:
                context["tweet"] = {
                    "author": tweet_data['author_username'],
                    "posted_at": tweet_data['created_at'],
                    "engagement": tweet_data['metrics'],
                    "author_metrics": tweet_data.get('author_metrics', {}),
                    "context_annotations": tweet_data.get('context_annotations', [])
                }
                logger.debug("Added tweet context")
            except Exception as e:
                logger.warning(f"Error processing tweet context: {str(e)}")

        return context

    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        unique_results = []
        seen_content = set()

        for result in results:
            content = f"{result['title']}{result['snippet']}"
            content_hash = hashlib.md5(content.encode()).hexdigest()

            if content_hash not in seen_content:
                unique_results.append(result)
                seen_content.add(content_hash)

        logger.debug(f"Removed {len(results) - len(unique_results)} duplicate results")
        return unique_results

    def search(self, query: str, tweet_data: Optional[Dict] = None) -> List[Dict]:
        logger.info(f"Starting search for query: {query}")
        search_queries = [
            query,
            f'fact check {query}',
            f'is "{query}" true',
            f'research about "{query}"'
        ]

        if tweet_data:
            search_queries.extend([
                f'fact check @{tweet_data["author_username"]} {query}',
                f'debunk {query}',
                f'verify {query}'
            ])

        all_results = []
        seen_urls = set()

        if tweet_data:
            tweet_source = {
                "title": f"Tweet by @{tweet_data['author_username']}",
                "snippet": tweet_data['text'],
                "url": f"https://twitter.com/user/status/{tweet_data['id']}",
                "domain": "twitter.com",
                "engine": "twitter",
                "metrics": tweet_data['metrics'],
                "created_at": tweet_data['created_at']
            }
            all_results.append(tweet_source)
            seen_urls.add(tweet_source['url'])
            logger.debug("Added original tweet as source")

        for search_query in search_queries:
            logger.info(f"Processing search query: {search_query}")
            results = []
            results.extend(self._get_google_results(search_query))
            results.extend(self._get_ddg_results(search_query))
            results.extend(self._get_wiki_results(search_query))

            for result in results:
                if result['url'] not in seen_urls:
                    all_results.append(result)
                    seen_urls.add(result['url'])

            if len(all_results) >= 15:
                logger.debug("Reached maximum number of results")
                break

            time.sleep(1)  # Rate limiting

        unique_results = self._remove_duplicates(all_results)
        logger.info(f"Search completed. Found {len(unique_results)} unique results")
        return unique_results[:15]