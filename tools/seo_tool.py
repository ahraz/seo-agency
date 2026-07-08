import re
import urllib.parse
from crewai.tools import tool


@tool("Extract Page Metadata")
def extract_page_metadata(url: str) -> str:
    """Extract basic SEO metadata from a web page URL: title, description, headings, and link count."""
    try:
        import requests
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        title = ""
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()

        description = ""
        desc_match = re.search(
            r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
            html, re.IGNORECASE
        )
        if desc_match:
            description = desc_match.group(1)

        h1_tags = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        h1s = [re.sub(r"<[^>]+>", "", h).strip() for h in h1_tags]

        link_count = len(re.findall(r"<a\s+", html, re.IGNORECASE))

        return (
            f"Title: {title}\n"
            f"Description: {description}\n"
            f"H1 tags: {', '.join(h1s) if h1s else 'None'}\n"
            f"Total links: {link_count}"
        )
    except Exception as e:
        return f"Error analyzing {url}: {e}"
