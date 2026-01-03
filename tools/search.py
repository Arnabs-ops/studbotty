from typing import Any, Dict, List
from tools.base import Tool
from config import config

class SearchTool(Tool):
    def __init__(self):
        super().__init__(name="search", description="Search the web.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }

    def execute(self, query: str) -> str:
        if config.OFFLINE_MODE:
            return "Offline mode enabled. Cannot perform web searches."
         
        try:
            from ddgs import DDGS
            results = list(DDGS().text(query, max_results=5))
            
            # Filter out irrelevant results
            filtered_results = []
            for r in results:
                title = r.get('title', '').strip()
                url = r.get('href', '').strip()
                summary = r.get('body', '').strip()
                
                # Skip results with empty or irrelevant content
                if title and url and summary and len(summary) > 20:
                    filtered_results.append({
                        "title": title,
                        "url": url,
                        "summary": summary
                    })
            
            # Format the results for better readability
            if not filtered_results:
                return "No relevant results found."
            
            output = "🔍 Search Results:\n\n"
            for idx, result in enumerate(filtered_results, start=1):
                output += f"{idx}. **{result['title']}**\n"
                output += f"   🔗 {result['url']}\n"
                output += f"   📝 {result['summary']}\n\n"
            
            return output.strip()
        except ImportError:
            return "❌ Error: `ddgs` package not installed. Install it using `pip install ddgs`."
        except Exception as e:
            return f"❌ Error: Search failed. Details: {str(e)}"
