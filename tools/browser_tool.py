import requests
from crewai.tools import tool


@tool("Browse Web Page")
def browse_web_page(url: str) -> str:
    """Fetch and return the text content of a web page. Useful for researching competitors or checking live sites."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text[:10000]
    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"
