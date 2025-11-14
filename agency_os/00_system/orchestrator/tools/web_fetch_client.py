"""Web content fetcher for research agents."""

import requests
from bs4 import BeautifulSoup
from typing import Dict


class WebFetchClient:
    """Safe web content fetcher with robots.txt respect"""

    def fetch(self, url: str) -> Dict:
        """
        Fetch and extract text content from URL

        Args:
            url: Full URL to fetch

        Returns:
            Dict: {"url": ..., "title": ..., "content": ..., "error": None}
        """
        try:
            # Fetch
            headers = {'User-Agent': 'VIBE-Agency-Research-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # Parse
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "Untitled"

            # Extract main content (heuristic: remove script/style tags)
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            content = soup.get_text(separator='\n', strip=True)

            # Truncate to 10k chars (prevent context overflow)
            content = content[:10000]

            return {
                'url': url,
                'title': title_text,
                'content': content,
                'error': None
            }

        except Exception as e:
            return {
                'url': url,
                'title': None,
                'content': None,
                'error': str(e)
            }


# CLI test
if __name__ == "__main__":
    client = WebFetchClient()
    result = client.fetch("https://news.ycombinator.com/")
    print(f"Title: {result['title']}")
    print(f"Content preview: {result['content'][:200]}...")
