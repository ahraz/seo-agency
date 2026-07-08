import json
import urllib.parse
import urllib.request
import re
from crewai.tools import tool


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for the given query. Returns top results with snippets."""
    try:
        encoded = urllib.parse.quote(query)
        # Use DuckDuckGo's HTML search (more reliable than the instant answer API)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")

        # Parse result snippets from DuckDuckGo HTML
        results = []
        # Find result blocks
        for result in re.findall(
            r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?'
            r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
            html,
            re.DOTALL,
        ):
            title = re.sub(r"<[^>]+>", "", result[0]).strip()
            snippet = re.sub(r"<[^>]+>", "", result[1]).strip()
            results.append(f"{title}\n  {snippet}")

        # Fallback: find links and snippets separately
        if not results:
            # Try extracting from WebResult blocks
            blocks = re.findall(
                r'class="result__body".*?class="result__title".*?href="([^"]*)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</',
                html,
                re.DOTALL,
            )
            for href, title_html, snippet_html in blocks[:8]:
                title = re.sub(r"<[^>]+>", "", title_html).strip()
                snippet = re.sub(r"<[^>]+>", "", snippet_html).strip()
                results.append(f"{title}\n  → {href[:80]}\n  {snippet}")

        if results:
            return "\n\n".join(results[:8])
        else:
            return "No search results found."
    except Exception as e:
        return f"Search error: {e}"
