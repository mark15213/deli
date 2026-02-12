# Subscription fetcher implementations
import logging
import re
from typing import List, Optional, Tuple
from datetime import datetime
import feedparser
import aiohttp
from bs4 import BeautifulSoup

from .base import BaseFetcher, BaseSubscriptionConfig, FetchedItem
from .configs import RSSSubscriptionConfig, HFDailyPapersConfig, AuthorBlogConfig

logger = logging.getLogger(__name__)


class RSSFetcher(BaseFetcher):
    """
    Fetcher for RSS/Atom feeds.
    """
    
    async def fetch_new_items(
        self,
        config: RSSSubscriptionConfig,
        connection_config: dict,
        since_cursor: Optional[str] = None
    ) -> Tuple[List[FetchedItem], Optional[str]]:
        """Fetch new items from an RSS feed."""
        feed_url = connection_config.get("url")
        if not feed_url:
            logger.error("No feed URL in connection_config")
            return [], None
        
        try:
            # Parse the feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed parsing warning: {feed.bozo_exception}")
            
            items = []
            new_cursor = since_cursor
            
            for entry in feed.entries[:config.max_items_per_sync]:
                # Get entry ID
                entry_id = entry.get("id") or entry.get("link") or entry.get("title")
                
                # Skip if we've seen this before (cursor-based)
                if since_cursor and entry_id == since_cursor:
                    break
                
                title = entry.get("title", "Untitled")
                
                # Apply filters
                if config.title_include_keywords:
                    if not any(kw.lower() in title.lower() for kw in config.title_include_keywords):
                        continue
                        
                if config.title_exclude_keywords:
                    if any(kw.lower() in title.lower() for kw in config.title_exclude_keywords):
                        continue
                
                # Get content length
                content = entry.get("summary", "") or entry.get("content", [{}])[0].get("value", "")
                if len(content) < config.content_min_length:
                    continue
                
                # Parse published date
                published = None
                if entry.get("published_parsed"):
                    published = datetime(*entry.published_parsed[:6])
                
                items.append(FetchedItem(
                    external_id=entry_id,
                    title=title,
                    url=entry.get("link", ""),
                    published_at=published,
                    metadata={
                        "author": entry.get("author"),
                        "summary": content[:500] if content else None,
                        "tags": [tag.get("term") for tag in entry.get("tags", [])],
                    }
                ))
                
                # Update cursor to first (newest) item
                if not new_cursor or items:
                    new_cursor = entry_id
            
            return items, new_cursor if items else since_cursor
            
        except Exception as e:
            logger.error(f"RSS fetch error: {e}")
            return [], since_cursor
    
    def get_snapshot_source_type(self) -> str:
        return "WEB_ARTICLE"
    
    def get_display_name(self) -> str:
        return "RSS Feed"


class HFDailyFetcher(BaseFetcher):
    """
    Fetcher for HuggingFace Daily Papers.
    Uses httpx for better proxy support.
    """
    
    HF_PAPERS_API = "https://huggingface.co/api/daily_papers"
    
    async def fetch_new_items(
        self,
        config: HFDailyPapersConfig,
        connection_config: dict,
        since_cursor: Optional[str] = None
    ) -> Tuple[List[FetchedItem], Optional[str]]:
        """Fetch papers from HuggingFace Daily Papers."""
        import httpx
        import os
        
        logger.info(f"Starting HF Daily Papers fetch with config: max_papers={config.max_papers_per_sync}, min_upvotes={config.min_upvotes}")
        
        # Get proxy from environment
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        
        try:
            # Use httpx
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, proxy=proxy) as client:
                if proxy:
                    logger.info(f"Requesting {self.HF_PAPERS_API} via proxy {proxy}")
                else:
                    logger.info(f"Requesting {self.HF_PAPERS_API} (direct)")
                resp = await client.get(self.HF_PAPERS_API)
                resp.raise_for_status()
                papers = resp.json()
                logger.info(f"Received {len(papers)} papers from HF API")
            
            # Sort by upvotes descending to get most popular first
            # Note: upvotes is inside paper object, not at top level
            papers = sorted(papers, key=lambda x: x.get("paper", {}).get("upvotes", 0) or 0, reverse=True)
            
            items = []
            new_cursor = since_cursor
            
            for paper in papers[:config.max_papers_per_sync]:
                paper_data = paper.get("paper", {})
                paper_id = paper_data.get("id")
                
                # Skip if we've seen this
                if since_cursor and paper_id == since_cursor:
                    logger.info(f"Reached cursor {since_cursor}, stopping")
                    break
                
                # Filter by upvotes - upvotes is inside paper_data
                upvotes = paper_data.get("upvotes", 0) or 0
                if upvotes < config.min_upvotes:
                    logger.debug(f"Skipping paper {paper_id} with {upvotes} upvotes (min: {config.min_upvotes})")
                    continue
                
                # Get arxiv URL
                arxiv_id = paper_data.get("arxivId") or paper_id
                url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else paper_data.get("url", "")
                
                items.append(FetchedItem(
                    external_id=paper_id,
                    title=paper_data.get("title", "Untitled Paper"),
                    url=url,
                    published_at=datetime.fromisoformat(paper.get("publishedAt").replace("Z", "+00:00")) if paper.get("publishedAt") else None,
                    metadata={
                        "authors": paper_data.get("authors", []),
                        "summary": paper_data.get("summary") if config.include_abstracts else None,
                        "upvotes": upvotes,
                        "arxiv_id": arxiv_id,
                    }
                ))
                
                if not new_cursor:
                    new_cursor = paper_id
            
            logger.info(f"Fetched {len(items)} items after filtering")
            return items, new_cursor if items else since_cursor
            
        except httpx.HTTPError as e:
            logger.error(f"HF Daily fetch HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"HF Daily fetch error: {e}", exc_info=True)
            raise
    
    def get_snapshot_source_type(self) -> str:
        return "ARXIV_PAPER"
    
    def get_display_name(self) -> str:
        return "HuggingFace Daily Papers"


class AuthorBlogFetcher(BaseFetcher):
    """
    Fetcher for monitoring author blogs for new posts.
    """
    
    async def fetch_new_items(
        self,
        config: AuthorBlogConfig,
        connection_config: dict,
        since_cursor: Optional[str] = None
    ) -> Tuple[List[FetchedItem], Optional[str]]:
        """Scrape blog page for new posts."""
        blog_url = connection_config.get("url")
        if not blog_url:
            logger.error("No blog URL in connection_config")
            return [], None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"User-Agent": "Deli-Bot/1.0"}
                async with session.get(blog_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status != 200:
                        logger.error(f"Blog fetch error: {resp.status}")
                        return [], since_cursor
                    
                    html = await resp.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            items = []
            new_cursor = since_cursor
            
            # Find post links
            link_elements = soup.select(config.link_selector or "a")
            
            for link_el in link_elements[:20]:  # Limit to 20 links
                href = link_el.get("href")
                if not href:
                    continue
                
                # Make absolute URL
                if href.startswith("/"):
                    from urllib.parse import urljoin
                    href = urljoin(blog_url, href)
                elif not href.startswith("http"):
                    continue
                
                # Apply URL pattern filter
                if config.url_pattern:
                    if not re.match(config.url_pattern, href):
                        continue
                
                # Skip if we've seen this
                if since_cursor and href == since_cursor:
                    break
                
                title = link_el.get_text(strip=True) or "Untitled Post"
                
                # Try to find date
                published = None
                if config.date_selector:
                    # Look for date near the link
                    parent = link_el.parent
                    if parent:
                        date_el = parent.select_one(config.date_selector)
                        if date_el:
                            # Try to parse datetime attribute or text
                            date_str = date_el.get("datetime") or date_el.get_text(strip=True)
                            # Basic date parsing (could be enhanced)
                            try:
                                published = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            except (ValueError, AttributeError):
                                pass
                
                items.append(FetchedItem(
                    external_id=href,
                    title=title,
                    url=href,
                    published_at=published,
                    metadata={
                        "source_blog": blog_url,
                    }
                ))
                
                if not new_cursor:
                    new_cursor = href
            
            return items, new_cursor if items else since_cursor
            
        except Exception as e:
            logger.error(f"Blog fetch error: {e}")
            return [], since_cursor
    
    def get_snapshot_source_type(self) -> str:
        return "WEB_ARTICLE"
    
    def get_display_name(self) -> str:
        return "Author Blog"
