import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.schemas.source_schemas import SourceType, SourceCategory, get_category_for_type
from app.schemas.detect_schemas import (
    DetectResponse, 
    PreviewMetadata, 
    FormSchema,
    SubscriptionHints,
    SubscriptionPreviewItem,
)
from app.subscriptions.registry import subscription_registry


class SourceDetector:
    """
    Detects the type and category of a source from user input.
    Routes to appropriate detection strategy based on URL patterns.
    """
    
    def detect(self, input_text: str, check_connectivity: bool = True) -> DetectResponse:
        input_text = input_text.strip()
        
        # 1. Check if it's a URL
        if not self._is_url(input_text):
            return self._handle_manual_note(input_text)
            
        url = input_text
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # 2. Strategy Routing by domain/pattern
        
        # Twitter/X
        if "twitter.com" in domain or "x.com" in domain:
            return self._handle_tweet(url)
        
        # GitHub
        elif "github.com" in domain:
            return self._handle_github(url)
        
        # arXiv
        elif "arxiv.org" in domain:
            return self._handle_arxiv(url)
        
        # HuggingFace
        elif "huggingface.co" in domain:
            return self._handle_huggingface(url, path)
        
        # Notion
        elif "notion.site" in domain or "notion.so" in domain:
            return self._handle_notion(url)
        
        # RSS/Feed detection
        elif self._looks_like_rss(url, path):
            return self._handle_rss(url, check_connectivity)
        
        # Medium
        elif "medium.com" in domain:
            return self._handle_medium(url, path)
        
        # Default: Web Article
        else:
            return self._handle_generic_web(url, check_connectivity)

    def _is_url(self, text: str) -> bool:
        return text.startswith("http://") or text.startswith("https://")
    
    def _looks_like_rss(self, url: str, path: str) -> bool:
        """Check if URL looks like an RSS feed."""
        rss_indicators = ['.rss', '/feed', '/rss', '.xml', '/atom']
        return any(ind in path for ind in rss_indicators)

    def _handle_manual_note(self, text: str) -> DetectResponse:
        """Handle plain text input as a manual note."""
        return DetectResponse(
            detected_type=SourceType.MANUAL_NOTE,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title="Quick Note",
                description=text[:200] + "..." if len(text) > 200 else text
            ),
            suggested_config={"tags": ["Note"]},
            form_schema=FormSchema(allow_frequency_setting=False)
        )

    def _handle_tweet(self, url: str) -> DetectResponse:
        """Handle Twitter/X URLs."""
        is_thread = "/status/" in url
        
        return DetectResponse(
            detected_type=SourceType.TWEET_THREAD,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title="Tweet/Thread",
                url=url,
                icon_url="https://abs.twimg.com/favicons/twitter.ico"
            ),
            suggested_config={"tags": ["Social", "X"]},
            form_schema=FormSchema(
                allow_frequency_setting=False,
                default_tags=["Social"]
            )
        )
        
    def _handle_github(self, url: str) -> DetectResponse:
        """Handle GitHub URLs - repos are snapshot by default."""
        parts = url.rstrip("/").split("/")
        repo_name = parts[-1] if len(parts) > 0 else "Unknown Repo"
        
        # Extract owner/repo
        owner = None
        if len(parts) >= 5:
            owner = parts[-2]
        
        return DetectResponse(
            detected_type=SourceType.GITHUB_REPO,
            category=SourceCategory.SNAPSHOT,  # GitHub repos are snapshot
            metadata=PreviewMetadata(
                title=f"GitHub: {repo_name}",
                description=f"Repository by {owner}" if owner else None,
                url=url,
                icon_url="https://github.githubassets.com/favicons/favicon.svg"
            ),
            suggested_config={
                "branch": "main",
                "tags": ["Code", "Dev"]
            },
            form_schema=FormSchema(
                allow_frequency_setting=False,
                default_tags=["Dev"]
            )
        )

    def _handle_arxiv(self, url: str) -> DetectResponse:
        """Handle arXiv paper URLs."""
        import xml.etree.ElementTree as ET
        
        # Extract ID: arxiv.org/abs/2310.00001 or arxiv.org/pdf/2310.00001.pdf
        arxiv_id = None
        match = re.search(r"arxiv\.org/(?:abs|pdf)/(\d+\.\d+)", url)
        if match:
            arxiv_id = match.group(1)
        
        title = "Arxiv Paper"
        description = None
        authors = []
        
        if arxiv_id:
            try:
                api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
                resp = requests.get(api_url, timeout=30)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    entry = root.find('atom:entry', ns)
                    if entry:
                        title_elem = entry.find('atom:title', ns)
                        if title_elem is not None:
                            title = title_elem.text.strip().replace('\n', ' ')
                            
                        summary_elem = entry.find('atom:summary', ns)
                        if summary_elem is not None:
                            description = summary_elem.text.strip().replace('\n', ' ')
                            
                        for author in entry.findall('atom:author', ns):
                            name = author.find('atom:name', ns)
                            if name is not None:
                                authors.append(name.text)
            except Exception as e:
                print(f"Error fetching arxiv data: {e}")

        author_str = None
        if authors:
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."

        return DetectResponse(
            detected_type=SourceType.ARXIV_PAPER,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title=title,
                description=description,
                author=author_str,
                url=url,
                icon_url="https://arxiv.org/favicon.ico"
            ),
            suggested_config={"tags": ["Research", "Paper"]},
            form_schema=FormSchema(
                allow_frequency_setting=False,
                default_tags=["Research"]
            )
        )

    def _handle_huggingface(self, url: str, path: str) -> DetectResponse:
        """Handle HuggingFace URLs."""
        # Check if it's the daily papers page
        if "/papers" in path and not re.search(r'/papers/\d+\.\d+', path):
            # This is the papers listing page - subscription
            return DetectResponse(
                detected_type=SourceType.HF_DAILY_PAPERS,
                category=SourceCategory.SUBSCRIPTION,
                metadata=PreviewMetadata(
                    title="HuggingFace Daily Papers",
                    description="Daily curated selection of top AI research papers",
                    url=url,
                    icon_url="https://huggingface.co/favicon.ico"
                ),
                suggested_config={"tags": ["Research", "AI"]},
                form_schema=FormSchema(
                    allow_frequency_setting=True,
                    default_tags=["Research", "Daily"]
                ),
                subscription_hints=SubscriptionHints(
                    suggested_frequency="DAILY",
                    estimated_items_per_day=10,
                    form_schema=subscription_registry.get_form_schema("HF_DAILY_PAPERS")
                )
            )
        
        # Specific paper link - treat as arXiv
        paper_match = re.search(r'/papers/(\d+\.\d+)', path)
        if paper_match:
            arxiv_id = paper_match.group(1)
            arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
            return self._handle_arxiv(arxiv_url)
        
        # Default HF page
        return DetectResponse(
            detected_type=SourceType.WEB_ARTICLE,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title="HuggingFace Page",
                url=url,
                icon_url="https://huggingface.co/favicon.ico"
            ),
            suggested_config={"tags": ["AI"]},
            form_schema=FormSchema(allow_frequency_setting=False)
        )

    def _handle_notion(self, url: str) -> DetectResponse:
        """Handle Notion URLs."""
        return DetectResponse(
            detected_type=SourceType.NOTION_KB,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title="Notion Page",
                url=url,
                icon_url="https://notion.so/images/favicon.ico"
            ),
            suggested_config={"tags": ["Notion", "Docs"]},
            form_schema=FormSchema(
                allow_frequency_setting=False,
                default_tags=["Docs"]
            )
        )
    
    def _handle_rss(self, url: str, check_connectivity: bool) -> DetectResponse:
        """Handle RSS/Atom feed URLs."""
        title = "RSS Feed"
        preview_items = []
        
        if check_connectivity:
            try:
                import feedparser
                feed = feedparser.parse(url)
                if feed.feed.get("title"):
                    title = feed.feed["title"]
                
                # Get preview items
                for entry in feed.entries[:3]:
                    preview_items.append(SubscriptionPreviewItem(
                        title=entry.get("title", "Untitled"),
                        url=entry.get("link", ""),
                        date=entry.get("published", None)
                    ))
            except Exception as e:
                print(f"Error parsing RSS: {e}")
        
        return DetectResponse(
            detected_type=SourceType.RSS_FEED,
            category=SourceCategory.SUBSCRIPTION,
            metadata=PreviewMetadata(
                title=title,
                url=url,
                icon_url=None
            ),
            suggested_config={"tags": ["Feed"]},
            form_schema=FormSchema(
                allow_frequency_setting=True,
                default_tags=["Feed"]
            ),
            subscription_hints=SubscriptionHints(
                suggested_frequency="DAILY",
                preview_items=preview_items,
                form_schema=subscription_registry.get_form_schema("RSS_FEED")
            )
        )

    def _handle_medium(self, url: str, path: str) -> DetectResponse:
        """Handle Medium URLs - distinguish between article and author profile."""
        # Check if it's an author profile (no article path)
        # Pattern: medium.com/@username or medium.com/@username?...
        is_profile = bool(re.match(r'^/@[\w-]+/?$', path))
        
        if is_profile:
            # Author blog subscription
            username = re.search(r'/@([\w-]+)', path)
            author = username.group(1) if username else "Unknown Author"
            
            return DetectResponse(
                detected_type=SourceType.AUTHOR_BLOG,
                category=SourceCategory.SUBSCRIPTION,
                metadata=PreviewMetadata(
                    title=f"Medium: @{author}",
                    description=f"Subscribe to posts by {author}",
                    url=url,
                    icon_url="https://medium.com/favicon.ico"
                ),
                suggested_config={"tags": ["Blog", "Medium"]},
                form_schema=FormSchema(
                    allow_frequency_setting=True,
                    default_tags=["Blog"]
                ),
                subscription_hints=SubscriptionHints(
                    suggested_frequency="DAILY",
                    form_schema=subscription_registry.get_form_schema("AUTHOR_BLOG")
                )
            )
        
        # Specific article
        return DetectResponse(
            detected_type=SourceType.WEB_ARTICLE,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title="Medium Article",
                url=url,
                icon_url="https://medium.com/favicon.ico"
            ),
            suggested_config={"tags": ["Blog", "Medium"]},
            form_schema=FormSchema(allow_frequency_setting=False)
        )

    def _handle_generic_web(self, url: str, check_connectivity: bool) -> DetectResponse:
        """Handle generic web URLs - default to web article snapshot."""
        title = "Web Page"
        description = None
        
        if check_connectivity:
            try:
                resp = requests.get(
                    url, 
                    timeout=3, 
                    headers={"User-Agent": "Deli-QuickAdd/1.0"}
                )
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    if soup.title:
                        title = soup.title.string
                    
                    # Try OG tags
                    og_title = soup.find("meta", property="og:title")
                    if og_title and og_title.get("content"):
                        title = og_title["content"]
                        
                    og_desc = soup.find("meta", property="og:description")
                    if og_desc and og_desc.get("content"):
                        description = og_desc["content"]
            except Exception as e:
                print(f"Error fetching url {url}: {e}")

        return DetectResponse(
            detected_type=SourceType.WEB_ARTICLE,
            category=SourceCategory.SNAPSHOT,
            metadata=PreviewMetadata(
                title=title,
                description=description,
                url=url
            ),
            suggested_config={"tags": ["Web"]},
            form_schema=FormSchema(
                allow_frequency_setting=False,
                default_tags=["Reading"]
            )
        )


# Singleton instance
source_detector = SourceDetector()
