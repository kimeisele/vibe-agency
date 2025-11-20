"""Google Custom Search API client for research agents."""

import os

import requests

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables only


class GoogleSearchClient:
    """Wrapper for Google Custom Search JSON API"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        if not self.api_key or not self.search_engine_id:
            raise ValueError("Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_ENGINE_ID")

        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, num_results: int = 10) -> list[dict]:
        """
        Execute Google search

        Args:
            query: Search query string
            num_results: Number of results (1-10)

        Returns:
            List of dicts: [{"title": ..., "snippet": ..., "url": ...}, ...]
        """
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(num_results, 10),  # API max is 10
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse results
            results = []
            for item in data.get("items", []):
                results.append(
                    {
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("link", ""),
                    }
                )

            return results

        except requests.HTTPError as e:
            # Try to get detailed error message from response
            error_detail = "Unknown error"
            try:
                error_json = e.response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", str(error_json["error"]))
                    error_code = error_json["error"].get("code", "unknown")
                    raise RuntimeError(
                        f"Google Search API error ({error_code}): {error_detail}\n"
                        f"Possible causes:\n"
                        f"  - Invalid API key (check GOOGLE_SEARCH_API_KEY)\n"
                        f"  - Invalid Search Engine ID (check GOOGLE_SEARCH_ENGINE_ID)\n"
                        f"  - API not enabled in Google Cloud Console\n"
                        f"  - Billing not enabled for the project"
                    )
            except Exception:
                pass
            raise RuntimeError(f"Google Search API error: {e}")
        except requests.RequestException as e:
            raise RuntimeError(f"Google Search API error: {e}")


# CLI test
if __name__ == "__main__":
    client = GoogleSearchClient()
    results = client.search("AI coding assistants 2024", num_results=5)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        print()
