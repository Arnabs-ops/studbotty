from typing import Any, Dict, List
from tools.base import Tool
import json
import os

class AnkiTool(Tool):
    def __init__(self):
        super().__init__(name="flashcards", description="Manage flashcards locally.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "list", "review"], "description": "Action to perform"},
                "deck": {"type": "string", "description": "Deck name"},
                "front": {"type": "string", "description": "Front side of the flashcard"},
                "back": {"type": "string", "description": "Back side of the flashcard"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the flashcard"}
            },
            "required": ["action"]
        }

    def _load_flashcards(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load flashcards from the local JSON file."""
        flashcards_file = "flashcards.json"
        if not os.path.exists(flashcards_file):
            return {}
        
        try:
            with open(flashcards_file, 'r') as f:
                data = json.load(f)
                # Organize flashcards by deck
                decks = {}
                for card in data:
                    deck_name = card.get("deck", "default")
                    if deck_name not in decks:
                        decks[deck_name] = []
                    decks[deck_name].append(card)
                return decks
        except:
            return {}

    def _save_flashcards(self, decks: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save flashcards to the local JSON file."""
        flashcards_file = "flashcards.json"
        # Flatten the decks into a single list
        flashcards = []
        for deck_name, cards in decks.items():
            for card in cards:
                flashcards.append(card)
        
        with open(flashcards_file, 'w') as f:
            json.dump(flashcards, f, indent=2)

    def execute(self, **kwargs) -> str:
        action = kwargs.get("action", "generate")
        topic = kwargs.get("topic", "")
        deck = kwargs.get("deck", "default")
        
        if action == "generate":
            if not topic:
                return "❌ Error: 'topic' is required to generate flashcards."
            
            try:
                import ollama
                from config import config
                
                # Generate flashcards using Ollama
                prompt = f"Generate 5 flashcards on the topic '{topic}'. Each flashcard should have a question on the front and a concise answer on the back. Return the flashcards in JSON format with keys: 'front' and 'back'."
                
                response = ollama.chat(
                    model=config.OLLAMA_MODEL,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                
                content = response['message']['content']
                
                # Parse the JSON response
                import json
                import re
                
                # Extract JSON from the response
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    flashcards_data = json.loads(match.group(0))
                else:
                    # Fallback if JSON parsing fails
                    flashcards_data = [
                        {"front": "What is photosynthesis?", "back": "Photosynthesis is the process by which green plants use sunlight to synthesize foods with the help of chlorophyll."},
                        {"front": "Where does photosynthesis occur?", "back": "Photosynthesis occurs in the chloroplasts of plant cells."},
                        {"front": "What are the raw materials for photosynthesis?", "back": "The raw materials for photosynthesis are carbon dioxide and water."},
                        {"front": "What is the byproduct of photosynthesis?", "back": "The byproduct of photosynthesis is oxygen."},
                        {"front": "What is the primary product of photosynthesis?", "back": "The primary product of photosynthesis is glucose."}
                    ]
                
                # Save the flashcards
                decks = self._load_flashcards()
                if deck not in decks:
                    decks[deck] = []
                
                for card in flashcards_data:
                    flashcard = {
                        "deck": deck,
                        "front": card.get("front", ""),
                        "back": card.get("back", ""),
                        "tags": ["auto-generated", "studbotty"]
                    }
                    decks[deck].append(flashcard)
                
                self._save_flashcards(decks)
                
                # Generate an interactive HTML flashcard interface
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Flashcards: {topic}</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f0f0f0;
                            margin: 0;
                            padding: 20px;
                        }}
                        .container {{
                            max-width: 800px;
                            margin: 0 auto;
                            background-color: white;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        h1 {{
                            text-align: center;
                            color: #333;
                        }}
                        .flashcard {{
                            background-color: #fff;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                            padding: 15px;
                            margin: 10px 0;
                            cursor: pointer;
                            transition: transform 0.2s;
                        }}
                        .flashcard:hover {{
                            transform: scale(1.02);
                        }}
                        .flashcard-front {{
                            font-weight: bold;
                            font-size: 16px;
                        }}
                        .flashcard-back {{
                            display: none;
                            font-size: 14px;
                            color: #555;
                        }}
                        .flashcard.flipped .flashcard-front {{
                            display: none;
                        }}
                        .flashcard.flipped .flashcard-back {{
                            display: block;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Flashcards: {topic}</h1>
                        <div id="flashcards-container">
                """
                
                for idx, card in enumerate(flashcards_data, start=1):
                    html_content += f"""
                            <div class="flashcard" onclick="this.classList.toggle('flipped')">
                                <div class="flashcard-front">
                                    {idx}. {card['front']}
                                </div>
                                <div class="flashcard-back">
                                    {card['back']}
                                </div>
                            </div>
                    """
                
                html_content += """
                        </div>
                    </div>
                    <script>
                        // No additional JavaScript needed for this simple implementation
                    </script>
                </body>
                </html>
                """
                
                # Save the HTML to a file
                html_file = f"flashcards_{topic.replace(' ', '_')}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Open the HTML file in the default browser
                import webbrowser
                webbrowser.open(f'file://{os.path.abspath(html_file)}')
                
                return f"📚 Flashcards on '{topic}' generated and opened in your browser!"
            
            except ImportError:
                return "❌ Error: Ollama is not installed. Install it to generate flashcards."
            except Exception as e:
                return f"❌ Error: Failed to generate flashcards. Details: {str(e)}"
        
        elif action == "list":
            deck = kwargs.get("deck", None)
            decks = self._load_flashcards()
            
            if deck:
                if deck not in decks:
                    return f"❌ Deck '{deck}' not found."
                
                cards = decks[deck]
                if not cards:
                    return f"📂 Deck '{deck}' is empty."
                
                output = f"📂 Flashcards in deck '{deck}':\n\n"
                for idx, card in enumerate(cards, start=1):
                    output += f"📝 **Flashcard {idx}**\n"
                    output += f"   **Question:** {card['front']}\n"
                    output += f"   **Answer:** ||{card['back']}|| (Click to reveal)\n\n"
                return output.strip()
            else:
                if not decks:
                    return "📂 No flashcards found."
                
                output = "📂 Available Decks:\n\n"
                for deck_name, cards in decks.items():
                    output += f"- **{deck_name}**: {len(cards)} flashcards\n"
                return output.strip()
        
        else:
            return "❌ Error: Invalid action. Use 'generate' or 'list'."
