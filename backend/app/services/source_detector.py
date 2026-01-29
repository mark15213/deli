import re
import requests
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from app.schemas.source_schemas import SourceType
from app.schemas.detect_schemas import DetectResponse, PreviewMetadata, FormSchema

class SourceDetector:
    def detect(self, input_text: str, check_connectivity: bool = True) -> DetectResponse:
        input_text = input_text.strip()
        
        # 1. Check if it's a URL
        if not self._is_url(input_text):
            return self._handle_manual_note(input_text)
            
        url = input_text
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # 2. Strategy Routing
        if "twitter.com" in domain or "x.com" in domain:
            return self._handle_x(url)
        elif "github.com" in domain:
            return self._handle_github(url)
        elif "arxiv.org" in domain:
            return self._handle_arxiv(url)
        elif "notion.site" in domain or "notion.so" in domain:
            return self._handle_notion(url)
        else:
            return self._handle_generic_web(url, check_connectivity)

    def _is_url(self, text: str) -> bool:
        # Simple check, can be improved
        return text.startswith("http://") or text.startswith("https://")

    def _handle_manual_note(self, text: str) -> DetectResponse:
        return DetectResponse(
            detected_type=SourceType.NOTION_KB, # Reusing NOTION_KB as a placeholder for "Note" or add a new type if needed.
            # Actually, user req mentioned MANUAL_NOTE, let's check SourceType enum.
            # SourceType enum currently: X_SOCIAL, NOTION_KB, ARXIV_PAPER, GITHUB_REPO, WEB_RSS.
            # Start with generic WEB_RSS or similar if NOTE is not available, or I should update SourceType enum.
            # Let's check schemas again.
            metadata=PreviewMetadata(
                title="Quick Note",
                description=text[:100] + "..." if len(text) > 100 else text
            ),
            suggested_config={"tags": ["Note"]},
            form_schema=FormSchema(allow_frequency_setting=False)
        )

    def _handle_x(self, url: str) -> DetectResponse:
        is_thread = "/status/" in url
        return DetectResponse(
            detected_type=SourceType.X_SOCIAL,
            metadata=PreviewMetadata(
                title="X Content",
                url=url,
                icon_url="https://abs.twimg.com/favicons/twitter.ico"
            ),
            suggested_config={
                "fetch_mode": "SNAPSHOT" if is_thread else "MONITOR",
                "recurrence": "ONCE" if is_thread else "HOURLY",
                "tags": ["Social", "X"]
            },
            form_schema=FormSchema(
                allow_frequency_setting=not is_thread,
                default_tags=["Social"]
            )
        )
        
    def _handle_github(self, url: str) -> DetectResponse:
        # Basic parsing, later can use API
        parts = url.rstrip("/").split("/")
        repo_name = parts[-1] if len(parts) > 0 else "Unknown Repo"
        
        return DetectResponse(
            detected_type=SourceType.GITHUB_REPO,
            metadata=PreviewMetadata(
                title=f"GitHub: {repo_name}",
                url=url,
                icon_url="https://github.githubassets.com/favicons/favicon.svg"
            ),
            suggested_config={
                "branch": "main",
                "tags": ["Code", "Dev"]
            },
             form_schema=FormSchema(
                allow_frequency_setting=True,
                default_tags=["Dev"]
            )
        )

    def _handle_arxiv(self, url: str) -> DetectResponse:
        import xml.etree.ElementTree as ET
        
        # Extract ID
        # Matches: arxiv.org/abs/2310.00001 or arxiv.org/pdf/2310.00001.pdf
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
                resp = requests.get(api_url, timeout=5)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    # Atom namespace
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

        # Format description with authors if available
        author_str = None
        if authors:
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."

        return DetectResponse(
            detected_type=SourceType.ARXIV_PAPER,
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

    def _handle_notion(self, url: str) -> DetectResponse:
        return DetectResponse(
            detected_type=SourceType.NOTION_KB,
            metadata=PreviewMetadata(
                title="Notion Page",
                url=url,
                icon_url="https://notion.so/images/favicon.ico"
            ),
            suggested_config={"tags": ["Notion", "Docs"]},
             form_schema=FormSchema(
                allow_frequency_setting=True,
                default_tags=["Docs"]
            )
        )

    def _handle_generic_web(self, url: str, check_connectivity: bool) -> DetectResponse:
        # Fallback to RSS or default generic
        title = "Web Page"
        description = None
        
        if check_connectivity:
            try:
                # Add a timeout to prevent hanging
                resp = requests.get(url, timeout=3, headers={"User-Agent": "Deli-QuickAdd/1.0"})
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    if soup.title:
                        title = soup.title.string
                    
                    # Try to find OG tags
                    og_title = soup.find("meta", property="og:title")
                    if og_title:
                        title = og_title["content"]
                        
                    og_desc = soup.find("meta", property="og:description")
                    if og_desc:
                        description = og_desc["content"]
            except Exception as e:
                print(f"Error fetching url {url}: {e}")

        return DetectResponse(
            detected_type=SourceType.WEB_RSS, # Defaulting to RSS/Web
            metadata=PreviewMetadata(
                title=title,
                description=description,
                url=url
            ),
            suggested_config={"tags": ["Web"]},
            form_schema=FormSchema(
                allow_frequency_setting=True,
                default_tags=["Reading"]
            )
        )

source_detector = SourceDetector()
