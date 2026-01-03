from typing import Any, Dict
from tools.base import Tool
from config import config
import webbrowser
import os
import re


class VizTool(Tool):
    def __init__(self):
        super().__init__(name="viz", description="Generate a diagram using Mermaid or Graphviz.")
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["mermaid", "graphviz"]},
                "content": {"type": "string"}
            },
            "required": ["kind", "content"]
        }

    def execute(self, kind: str, content: str) -> str:
        """Generate a diagram using AI to create Mermaid or Graphviz code."""
        
        try:
            import ollama
            
            # Check if Ollama service is available
            try:
                # Test if Ollama service is running
                ollama.list()
            except Exception as e:
                return f"❌ Ollama service is not available or not running. Please start Ollama service. Error: {str(e)}"
            
            # Step 1: Research the topic to get structured data
            research_prompt = f"""Analyze the following topic for a detailed diagram: {content}
            
            Provide a comprehensive analysis including:
            1. Main processes/steps involved
            2. Key components and their roles
            3. Inputs and outputs for each step
            4. How the steps connect to each other
            5. Important intermediate products
            
            Format as a structured list with clear labels. Be specific and informative.
            
            IMPORTANT: Focus on the specific topic provided, not generic examples.
            """
              
            research_response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': research_prompt}]
            )
            research_data = research_response['message']['content'].strip()
              
            # Step 2: Generate Diagram based on research
            if kind == "mermaid":
                prompt = f"""Generate a detailed Mermaid flowchart based on this analysis:
{research_data}

IMPORTANT: Create a comprehensive, informative diagram that clearly shows the process flow.

Requirements:
1. Use descriptive node labels that explain what each step/component does
2. Show the logical flow from start to finish
3. Include key intermediate products and outputs
4. Make connections clear and meaningful
5. Use specific, topic-relevant labels - NO generic labels like A, B, C, etc.

Syntax Rules:
- Start with `graph TD`
- Node IDs must be ONE WORD (No spaces!). Use CamelCase (e.g. LightEnergy).
- Node Labels can have spaces and should be descriptive (e.g. LightEnergy[Light Energy Absorption]).
- Do NOT use same ID for different nodes.
- DO NOT use single letters like A, B, C, etc. as node IDs - use meaningful names!

Node Types:
- ([Start/End]) for beginning and end points
- [/Input/Output/] for inputs and outputs
- [Process Step] for actions/procedures
- {{Decision?}} for decision points

Example for photosynthesis:
graph TD
    Sunlight([Sunlight]) --> LightReactions[Light Reactions]
    LightReactions --> ATP[ATP Production]
    LightReactions --> NADPH[NADPH Production]
    ATP --> CalvinCycle[Calvin Cycle]
    NADPH --> CalvinCycle
    CalvinCycle --> Glucose([Glucose])

Generate ONLY the Mermaid code. Do NOT include markdown code fences.
"""
            else:
                prompt = f"""Generate Graphviz DOT code based on this analysis:
{research_data}

IMPORTANT: Return ONLY the DOT code, nothing else. No explanations, no markdown code fences.
"""
              
            response = ollama.chat(
                model=config.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': prompt}]
            )
            code = response['message']['content'].strip()
              
            # Clean up common formatting issues
            # Remove markdown code fences if present
            if code.startswith('```'):
                lines = code.split('\n')
                # Remove first line (```mermaid or ```dot)
                lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines).strip()
            
            # Remove any trailing text that's not part of the Mermaid code
            # Look for common patterns that indicate the end of Mermaid code
            mermaid_end_patterns = [
                '```',
                'Final Answer:',
                'The final answer is',
                '$\\boxed{'
            ]
            
            lines = code.split('\n')
            mermaid_lines = []
            for line in lines:
                line_stripped = line.strip()
                if any(pattern in line_stripped for pattern in mermaid_end_patterns):
                    break
                mermaid_lines.append(line)
            
            code = '\n'.join(mermaid_lines).strip()
              
            # Fix common Mermaid syntax errors from smaller models
            # Remove 'end' keyword if there are no subgraphs (common hallucination)
            if 'subgraph' not in code.lower():
                lines = code.split('\n')
                lines = [line for line in lines if line.strip().lower() != 'end']
                code = '\n'.join(lines).strip()
              
            # Generate viewable URL using Mermaid.ink service
            if kind == "mermaid":
                # Apply additional Mermaid syntax validation and correction
                code = self._fix_mermaid_syntax(code)

                # Ensure the Mermaid code is valid
                if not code.startswith('graph'):
                    code = f"graph TD\n{code}"

                # Save the Mermaid code to a local HTML file for viewing
                html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StudBotty - Mermaid Diagram</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {{
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333;
            --border-radius: 12px;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .diagram-container {{
            background: var(--card-bg);
            border-radius: var(--border-radius);
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: var(--shadow);
            border: 1px solid #e9ecef;
        }}
        
        .mermaid {{
            text-align: center;
            overflow-x: auto;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }}
        
        .footer a {{
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .diagram-container {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Mermaid Diagram</h1>
            <p>Generated with StudBotty AI</p>
        </div>
        <div class="content">
            <div class="diagram-container">
                <div class="mermaid">
                    {code}
                </div>
            </div>
        </div>
        <div class="footer">
            <p>✨ Generated by <a href="https://github.com/studbotty" target="_blank">StudBotty</a> | <a href="#" onclick="window.print()">Print Diagram</a></p>
        </div>
    </div>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#667eea',
                primaryTextColor: '#fff',
                primaryBorderColor: '#764ba2',
                lineColor: '#667eea',
                secondaryColor: '#f8f9fa',
                tertiaryColor: '#ffffff'
            }}
        }});
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            const mermaidElements = document.querySelectorAll('.mermaid');
            mermaidElements.forEach(element => {{
                element.addEventListener('click', function(e) {{
                    if (e.target.tagName === 'text' || e.target.tagName === 'tspan') {{
                        const text = e.target.textContent || e.target.innerText;
                        if (text) {{
                            // Add a subtle highlight effect
                            e.target.style.fill = '#667eea';
                            setTimeout(() => {{
                                e.target.style.fill = '#333';
                            }}, 500);
                        }}
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
"""
                  
                # Save the HTML to a file
                html_file = "diagram.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                  
                # Open the HTML file in the default browser
                try:
                    webbrowser.open(f'file://{os.path.abspath(html_file)}')
                    opened_msg = "\n✅ Diagram opened in browser."
                except Exception as e:
                    opened_msg = f"\n⚠️ Could not open browser automatically: {e}\n📁 You can manually open the file: {os.path.abspath(html_file)}"

                return f"""📊 Diagram generated successfully!{opened_msg}

The diagram has been saved to `diagram.html` and opened in your browser.

```mermaid
{code}
```"""
            else:
                # For Graphviz, just provide the code
                return f"""📊 Here's your Graphviz diagram:

```dot
{code}
```

You can paste this into: https://dreampuf.github.io/GraphvizOnline/"""
              
        except ImportError:
            return "❌ Ollama is not installed. Please install it to use visualization features.\n\n💡 You can install Ollama from: https://ollama.ai/"
        except Exception as e:
            return f"❌ Sorry, I couldn't generate the diagram. Error: {str(e)}\n\n🔧 Troubleshooting tips:\n1. Make sure Ollama is installed and running\n2. Try running 'ollama serve' to start the service\n3. Check that the model '{config.OLLAMA_MODEL}' is available with 'ollama list'"

    def _fix_mermaid_syntax(self, code: str) -> str:
        """Fix common Mermaid syntax errors with comprehensive validation."""
        if not code or not isinstance(code, str):
            return "graph TD\n    A[Empty Response]"
        
        lines = code.split('\n')
        fixed_lines = []
        graph_found = False
        defined_nodes = set()
        referenced_nodes = set()
        
        # First pass: collect all referenced nodes
        for line in lines:
            line = line.strip()
            if not line or line.startswith('graph') or line.startswith('//') or line.startswith('%%'):
                continue
            
            # Find all node references in connections
            if ' --> ' in line:
                parts = line.split(' --> ')
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    
                    # Extract node IDs
                    source_match = re.match(r'^([A-Za-z0-9_]+)', source)
                    target_match = re.match(r'^([A-Za-z0-9_]+)', target)
                    
                    if source_match:
                        referenced_nodes.add(source_match.group(1))
                    if target_match:
                        referenced_nodes.add(target_match.group(1))
        
        # Second pass: fix lines and collect defined nodes
        for line in lines:
            original_line = line
            line = line.strip()
            if not line:
                continue
                
            # Skip empty lines and comments
            if line.startswith('//') or line.startswith('%%'):
                fixed_lines.append(original_line)
                continue
            
            # Ensure we have a graph declaration
            if line.startswith('graph '):
                graph_found = True
                fixed_lines.append(line)
                continue
                
            # Fix "Start: Text" or "End: Text" style definitions
            colon_pattern = r'^([A-Za-z0-9_]+):\s*(.+)$'
            match = re.match(colon_pattern, line)
            if match:
                node_id, label = match.groups()
                # Clean the label - remove problematic characters
                clean_label = re.sub(r'[{}]', '', label).strip()
                # Create a proper node definition
                line = f"{node_id}[{clean_label}]"
                defined_nodes.add(node_id)
            
            # Fix malformed "node Circle[Sun] {Light Energy}" style definitions
            node_pattern = r'^node\s+([A-Za-z0-9_]+)\[([^\]]+)\]\s*\{[^}]*\}\s*$'
            match = re.match(node_pattern, line)
            if match:
                node_id, label = match.groups()
                # Clean label - remove problematic characters
                clean_label = re.sub(r'[{}]', '', label)
                line = f"{node_id}[{clean_label}]"
                defined_nodes.add(node_id)
            
            # Fix "node {Blue} Label[Text]" style definitions  
            style_node_pattern = r'^node\s*\{[^}]*\}\s*([A-Za-z0-9_]+)\[([^\]]+)\]\s*$'
            match = re.match(style_node_pattern, line)
            if match:
                node_id, label = match.groups()
                clean_label = re.sub(r'[{}]', '', label)
                line = f"{node_id}[{clean_label}]"
                defined_nodes.add(node_id)
            
            # Fix standalone "node" statements
            if line.startswith('node ') and '[' not in line:
                content = line[5:].strip()
                if content:
                    # Create safe node ID and label
                    content_clean = re.sub(r'[^A-Za-z0-9_\s]', '', content).strip()
                    if content_clean:
                        # Replace spaces with underscores for node ID, limit length
                        node_id = re.sub(r'\s+', '_', content_clean)[:20]
                        # Clean label for display
                        clean_label = re.sub(r'[{}]', '', content_clean)
                        line = f"{node_id}[{clean_label}]"
                        defined_nodes.add(node_id)
                    else:
                        continue
                else:
                    continue
            
            # Fix standalone arrows
            if line.strip() == '-->':
                continue
            if line.startswith('--> '):
                continue
            if line.endswith(' -->'):
                continue
            
            # Fix malformed connections
            if ' --> --> ' in line:
                line = line.replace(' --> --> ', ' --> ')
            if line.endswith(' --> -->'):
                line = line[:-4]
            if line.startswith(' --> --> '):
                line = line[4:]
            
            # Remove duplicate connections
            if line in fixed_lines:
                continue
            
            # Fix malformed node connections with comprehensive cleaning
            if ' --> ' in line and not line.startswith('graph'):
                parts = line.split(' --> ')
                if len(parts) == 2:
                    source, target = parts
                    
                    # Extract node IDs from source and target
                    source_match = re.match(r'^([A-Za-z0-9_]+)', source.strip())
                    target_match = re.match(r'^([A-Za-z0-9_]+)', target.strip())
                    
                    if source_match and target_match:
                        source_id = source_match.group(1)
                        target_id = target_match.group(1)
                        
                        # Ensure both nodes are defined or will be defined
                        line = f"{source_id} --> {target_id}"
                    else:
                        # Skip malformed connection lines
                        continue
            
            # Remove problematic lines
            if re.match(r'^node\s*$', line):
                continue
            
            # Skip lines that are clearly malformed
            if line.count('[') != line.count(']') or line.count('{') != line.count('}'):
                continue
                
            # Check if this line defines a node
            node_match = re.match(r'^([A-Za-z0-9_]+)\[', line)
            if node_match:
                defined_nodes.add(node_match.group(1))
                
            fixed_lines.append(line)
        
        # If no graph declaration found, add one
        if not graph_found and fixed_lines:
            fixed_lines.insert(0, "graph TD")
        elif not fixed_lines:
            return "graph TD\n    A[No valid diagram content generated]\n    A --> B[Please try again]"
        
        # Add missing node definitions and improve generic ones
        missing_nodes = referenced_nodes - defined_nodes
        if missing_nodes:
            # Insert missing node definitions after the graph declaration
            graph_index = next(i for i, line in enumerate(fixed_lines) if line.startswith('graph'))
            for node_id in sorted(missing_nodes):
                # Create a descriptive node definition for missing nodes
                clean_label = self._generate_descriptive_label(node_id)
                fixed_lines.insert(graph_index + 1, f"    {node_id}[{clean_label}]")
                defined_nodes.add(node_id)
        
        # Improve generic node labels
        improved_lines = []
        for line in fixed_lines:
            # Check if this is a node definition with a generic label
            generic_pattern = r'^\s*([A-Za-z0-9_]+)\[(Process|Input|Output|Node|Step)\]$'
            match = re.match(generic_pattern, line)
            if match:
                node_id, generic_label = match.groups()
                # Generate a better label based on context
                better_label = self._generate_descriptive_label(node_id)
                line = f"    {node_id}[{better_label}]"
            improved_lines.append(line)
        
        fixed_lines = improved_lines
        
        # Join and clean up
        fixed_code = '\n'.join(fixed_lines)
        
        # Remove multiple consecutive empty lines
        while '\n\n\n' in fixed_code:
            fixed_code = fixed_code.replace('\n\n\n', '\n\n')
            
        # Final validation - ensure all referenced nodes are defined
        lines = fixed_code.split('\n')
        defined_nodes = set()
        referenced_nodes = set()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('graph') or line.startswith('//') or line.startswith('%%'):
                continue
            
            # Find defined nodes
            node_match = re.match(r'^([A-Za-z0-9_]+)\[', line)
            if node_match:
                defined_nodes.add(node_match.group(1))
            
            # Find referenced nodes in connections
            if ' --> ' in line:
                parts = line.split(' --> ')
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    
                    source_match = re.match(r'^([A-Za-z0-9_]+)', source)
                    target_match = re.match(r'^([A-Za-z0-9_]+)', target)
                    
                    if source_match:
                        referenced_nodes.add(source_match.group(1))
                    if target_match:
                        referenced_nodes.add(target_match.group(1))
        
        # Add any missing node definitions
        missing_nodes = referenced_nodes - defined_nodes
        if missing_nodes:
            # Find the graph declaration line
            graph_line_index = next(i for i, line in enumerate(lines) if line.startswith('graph'))
            
            # Insert missing node definitions after the graph line
            for node_id in sorted(missing_nodes):
                descriptive_label = self._generate_descriptive_label(node_id)
                lines.insert(graph_line_index + 1, f"    {node_id}[{descriptive_label}]")
                graph_line_index += 1
        
        # Final syntax validation and cleanup
        final_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are clearly malformed
            if line.count('[') != line.count(']') or line.count('{') != line.count('}'):
                continue
            
            # Ensure proper subgraph closing
            if line.startswith('subgraph') and not line.endswith('end'):
                final_lines.append(line)
                continue
            
            final_lines.append(line)
        
        return '\n'.join(final_lines).strip()
    
    def _generate_descriptive_label(self, node_id: str) -> str:
        """Generate a more descriptive label for a node ID."""
        # Common mappings for better labels
        label_map = {
            'glycolysis': 'Glycolysis',
            'krebs': 'Krebs Cycle',
            'citric': 'Citric Acid Cycle',
            'electron': 'Electron Transport',
            'atp': 'ATP Production',
            'nadh': 'NADH Production',
            'fadh2': 'FADH2 Production',
            'glucose': 'Glucose',
            'pyruvate': 'Pyruvate',
            'acetyl': 'Acetyl-CoA',
            'co2': 'Carbon Dioxide',
            'h2o': 'Water',
            'oxygen': 'Oxygen',
            'mitochondria': 'Mitochondria',
            'cellular': 'Cellular Respiration',
            'respiration': 'Cellular Respiration',
            'photosynthesis': 'Photosynthesis',
            'chlorophyll': 'Chlorophyll',
            'light': 'Light Reactions',
            'dark': 'Calvin Cycle',
            'carbon': 'Carbon Fixation',
        }
        
        # Convert node_id to lowercase for lookup
        node_lower = node_id.lower()
        
        # Check for direct matches
        if node_lower in label_map:
            return label_map[node_lower]
        
        # Check for partial matches
        for key, value in label_map.items():
            if key in node_lower:
                return value
        
        # Default: clean up the node_id
        clean_label = re.sub(r'[_-]', ' ', node_id)
        return clean_label.title()
    
    def _validate_mermaid_code(self, code: str) -> tuple[bool, str]:
        """Validate Mermaid code and return (is_valid, error_message)"""
        if not code:
            return False, "Empty code provided"
        
        if not code.startswith('graph'):
            return False, "Missing graph declaration"
        
        # Check for balanced brackets and braces
        bracket_count = 0
        brace_count = 0
        paren_count = 0
        
        for char in code:
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            
            # Early exit if any count goes negative (unmatched closing)
            if bracket_count < 0 or brace_count < 0 or paren_count < 0:
                return False, "Unmatched brackets, braces, or parentheses"
        
        # Check if all counts are balanced
        if bracket_count != 0 or brace_count != 0 or paren_count != 0:
            return False, "Unbalanced brackets, braces, or parentheses"
        
        return True, ""
    
    def visualize_flashcards(self, flashcards: list) -> str:
        """Visualize flashcards as a Mermaid diagram showing questions and answers."""
        if not flashcards:
            return "❌ No flashcards provided to visualize."
        
        try:
            # Convert flashcards to a format suitable for visualization
            content = f"Create a study diagram for these {len(flashcards)} flashcards:\n\n"
            
            for i, card in enumerate(flashcards, 1):
                front = str(card.get('front', 'No question')).strip()
                back = str(card.get('back', 'No answer')).strip()
                content += f"Card {i}: {front} → {back}\n"
            
            # Use the existing execute method to generate the diagram
            result = self.execute(kind="mermaid", content=content)
            
            # If successful, rename the file to be more specific for flashcards
            if "diagram.html" in result and os.path.exists("diagram.html"):
                flashcard_html_file = "flashcards_visualization.html"
                try:
                    os.rename("diagram.html", flashcard_html_file)
                    # Update the result message to reflect the new filename
                    result = result.replace("diagram.html", "flashcards_visualization.html")
                except Exception:
                    # If rename fails, keep the original filename
                    pass
            
            return result
            
        except Exception as e:
            return f"❌ Error visualizing flashcards: {str(e)}"

    def _create_fallback_diagram(self, topic: str) -> str:
        """Create a simple fallback diagram when generation fails"""
        safe_topic = re.sub(r'[^A-Za-z0-9_\s]', '', topic).strip()[:30]
        return f"""graph TD
    A[{safe_topic}] --> B[Information unavailable]
    A --> C[Please try again]
    style A fill:#ffcccc
    style B fill:#ffffcc
    style C fill:#ccffcc"""
