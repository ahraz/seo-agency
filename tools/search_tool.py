import json
import urllib.parse
import urllib.request
from crewai.tools import tool


@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for the given query using a public search API. Returns top results."""
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            results = []
            if "AbstractText" in data and data["AbstractText"]:
                results.append(data["AbstractText"])
            if "RelatedTopics" in data:
                for topic in data["RelatedTopics"][:5]:
                    if isinstance(topic, dict) and "Text" in topic:
                        results.append(topic["Text"])
            return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {e}"
