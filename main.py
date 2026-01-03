import logging
import sys
import pyttsx3
import re
import os
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.markup import escape
from config import config
from agent import Agent

# Check if terminal supports rich formatting
force_simple_output = os.getenv('STUDBOTTY_SIMPLE', 'false').lower() == 'true'
if not force_simple_output:
    # Try to detect if terminal supports ANSI codes
    # Modern Windows terminals (Windows Terminal, PowerShell, etc.) support ANSI
    if sys.platform == 'win32':
        # Most modern Windows terminals support rich formatting
        # Try to initialize colorama for better Windows terminal support
        try:
            import colorama
            colorama.init()
        except ImportError:
            # colorama not available, but that's ok - rich can still work
            pass
        except Exception:
            # Colorama initialization failed, but we'll still try rich formatting
            pass

# Setup logging with fallback
if force_simple_output:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[logging.StreamHandler()]
    )
else:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )

logger = logging.getLogger("studbotty")
console = Console(force_terminal=not force_simple_output, legacy_windows=force_simple_output)

# Initialize TTS engine with natural voice settings
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 120)  # Slower speech rate for natural sound
tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# Try to set a female voice if available (usually more natural sounding)
voices = tts_engine.getProperty('voices')
if len(voices) > 1:
    tts_engine.setProperty('voice', voices[1].id)  # Often female voice

voice_mode = False

def print_welcome():
    if force_simple_output:
        print("=" * 30)
        print("    StudBotty")
        print("=" * 30)
        print("Welcome to StudBotty!")
        print("Your AI Study Companion.")
        print("Type :help for onboarding.")
        print("=" * 30)
    else:
        console.print(Panel.fit(
            "[bold blue]Welcome to StudBotty![/bold blue]\n"
            "Your AI Study Companion.\n"
            "Type [bold cyan]:help[/bold cyan] for onboarding.",
            title="StudBotty",
            border_style="blue"
        ))

def print_help():
    """Interactive onboarding system for StudBotty tools and commands."""
    if force_simple_output:
        # Simple text version for basic terminals
        print("\n" + "=" * 60)
        print("           🚀 STUDBOTTY ONBOARDING GUIDE 🚀")
        print("=" * 60)
        print("\n🎯 QUICK START:")
        print("   Type any question or command to get started!")
        print("\n📋 AVAILABLE TOOLS:")
        print("   • Quiz Tool     - Test your knowledge with interactive quizzes")
        print("   • Math Tool     - Solve equations and calculations")
        print("   • Viz Tool      - Create diagrams and visualizations")
        print("   • Search Tool   - Find information online")
        print("   • Files Tool    - Read and analyze files")
        print("   • Flashcards    - Create study flashcards")
        print("   • Chat Tool     - General Q&A and explanations")
        print("   • TTS Tool      - Text-to-speech for reading aloud")
        print("\n🎮 COMMANDS:")
        print("   :help          - Show this guide")
        print("   :quit          - Exit StudBotty")
        print("   :tools         - List all available tools")
        print("   :profile       - Manage your profile")
        print("   :topics        - Show important topics")
        print("   :preferences   - Set learning preferences")
        print("\n🔊 VOICE MODE:")
        print("   enable voice mode    - Turn on speech output")
        print("   disable voice mode   - Turn off speech output")
        print("\n💡 EXAMPLES:")
        print("   'Explain photosynthesis'           → Chat Tool")
        print("   'Quiz me on python'                → Quiz Tool")
        print("   'Solve 2 + 2'                      → Math Tool")
        print("   'Visualize a binary tree'          → Viz Tool")
        print("   'Search quantum computing'         → Search Tool")
        print("   'Read file.txt'                    → Files Tool")
        print("   'Create flashcards on biology'     → Flashcards")
        print("   'Speak hello world'                → TTS Tool")
        print("\n🎯 TIPS:")
        print("   • Be specific with your requests")
        print("   • Use natural language")
        print("   • Try different tools for different needs")
        print("   • Enable voice mode for audio learning")
        print("\n" + "=" * 60)
        print("           Ready to start learning? 📚")
        print("=" * 60)
    else:
        # Rich formatted version with colors and emojis
        console.print(Panel.fit(
            "[bold blue]🚀 STUDBOTTY ONBOARDING GUIDE 🚀[/bold blue]",
            border_style="blue"
        ))
        
        console.print("\n[bold]🎯 QUICK START:[/bold]")
        console.print("   Type any question or command to get started!")
        
        console.print("\n[bold]📋 AVAILABLE TOOLS:[/bold]")
        console.print("   • [green]Quiz Tool[/green]     - Test your knowledge with interactive quizzes")
        console.print("   • [green]Math Tool[/green]     - Solve equations and calculations")
        console.print("   • [green]Viz Tool[/green]      - Create diagrams and visualizations")
        console.print("   • [green]Search Tool[/green]   - Find information online")
        console.print("   • [green]Files Tool[/green]    - Read and analyze files")
        console.print("   • [green]Flashcards[/green]    - Create study flashcards")
        console.print("   • [green]Chat Tool[/green]     - General Q&A and explanations")
        console.print("   • [green]TTS Tool[/green]      - Text-to-speech for reading aloud")
        
        console.print("\n[bold]🎮 COMMANDS:[/bold]")
        console.print("   [cyan]:help[/cyan]          - Show this guide")
        console.print("   [cyan]:quit[/cyan]          - Exit StudBotty")
        console.print("   [cyan]:tools[/cyan]         - List all available tools")
        console.print("   [cyan]:profile[/cyan]       - Manage your profile")
        console.print("   [cyan]:topics[/cyan]        - Show important topics")
        console.print("   [cyan]:preferences[/cyan]   - Set learning preferences")
        
        console.print("\n[bold]🔊 VOICE MODE:[/bold]")
        console.print("   [yellow]enable voice mode[/yellow]    - Turn on speech output")
        console.print("   [yellow]disable voice mode[/yellow]   - Turn off speech output")
        
        console.print("\n[bold]💡 EXAMPLES:[/bold]")
        console.print("   [italic]'Explain photosynthesis'[/italic]           → [green]Chat Tool[/green]")
        console.print("   [italic]'Quiz me on python'[/italic]                → [green]Quiz Tool[/green]")
        console.print("   [italic]'Solve 2 + 2'[/italic]                      → [green]Math Tool[/green]")
        console.print("   [italic]'Visualize a binary tree'[/italic]          → [green]Viz Tool[/green]")
        console.print("   [italic]'Search quantum computing'[/italic]         → [green]Search Tool[/green]")
        console.print("   [italic]'Read file.txt'[/italic]                    → [green]Files Tool[/green]")
        console.print("   [italic]'Create flashcards on biology'[/italic]     → [green]Flashcards[/green]")
        console.print("   [italic]'Speak hello world'[/italic]                → [green]TTS Tool[/green]")
        
        console.print("\n[bold]🎯 TIPS:[/bold]")
        console.print("   • Be specific with your requests")
        console.print("   • Use natural language")
        console.print("   • Try different tools for different needs")
        console.print("   • Enable voice mode for audio learning")
        
        console.print(Panel.fit(
            "[bold green]Ready to start learning? 📚[/bold green]",
            border_style="green"
        ))

def speak(text):
    """Convert text to speech, excluding emojis"""
    try:
        # Remove emojis from text using regex
        import re
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
            "\U00002702-\U000027B0"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f\u200d"
            "\u3030"
            "]+", flags=re.UNICODE
        )
        clean_text = emoji_pattern.sub(r'', text)
        
        tts_engine.say(clean_text)
        tts_engine.runAndWait()
    except Exception as e:
        logger.error(f"TTS Error: {e}")

def _handle_profile_command(user_input: str, agent, force_simple_output: bool, console):
    """Handle profile-related commands."""
    context_manager = agent.tools.get('context_manager')
    if not context_manager:
        if force_simple_output:
            print("Context manager not available")
        else:
            console.print("[red]Context manager not available[/red]")
        return
        
    parts = user_input.split(':', 2)
    if len(parts) < 3:
        if force_simple_output:
            print("Usage: :profile set key value OR :profile get key OR :profile show")
        else:
            console.print("[yellow]Usage:[/yellow] :profile set key value OR :profile get key OR :profile show")
        return
        
    action = parts[1].strip()
    
    if action == "set":
        key_value = parts[2].split(' ', 1)
        if len(key_value) == 2:
            key, value = key_value
            result = context_manager.execute('set_profile', key=key.strip(), value=value.strip())
            if force_simple_output:
                print(f"Profile set: {key} = {value}")
            else:
                console.print(f"[green]Profile set:[/green] {key} = {value}")
        else:
            if force_simple_output:
                print("Usage: :profile set key value")
            else:
                console.print("[yellow]Usage:[/yellow] :profile set key value")
    elif action == "get":
        key = parts[2].strip()
        value = context_manager.execute('get_profile', key=key)
        if force_simple_output:
            print(f"{key}: {value}")
        else:
            console.print(f"[bold]{key}:[/bold] {value}")
    elif action == "show":
        profile = context_manager.execute('get_profile')
        if force_simple_output:
            print("User Profile:")
            for key, value in profile.items():
                print(f"  {key}: {value}")
        else:
            console.print("[bold]User Profile:[/bold]")
            for key, value in profile.items():
                console.print(f"  [cyan]{key}:[/cyan] {value}")

def _handle_topics_command(agent, force_simple_output: bool, console):
    """Handle topics-related commands."""
    context_manager = agent.tools.get('context_manager')
    if not context_manager:
        if force_simple_output:
            print("Context manager not available")
        else:
            console.print("[red]Context manager not available[/red]")
        return
        
    topics = context_manager.execute('get_topics')
    if force_simple_output:
        print("Important Topics:")
        for i, topic in enumerate(topics, 1):
            print(f"  {i}. {topic}")
    else:
        console.print("[bold]Important Topics:[/bold]")
        for i, topic in enumerate(topics, 1):
            console.print(f"  {i}. [green]{topic}[/green]")

def _handle_preferences_command(user_input: str, agent, force_simple_output: bool, console):
    """Handle preferences-related commands."""
    context_manager = agent.tools.get('context_manager')
    if not context_manager:
        if force_simple_output:
            print("Context manager not available")
        else:
            console.print("[red]Context manager not available[/red]")
        return
        
    parts = user_input.split(':', 2)
    if len(parts) < 3:
        # Show all preferences
        preferences = context_manager.execute('get_preferences')
        if force_simple_output:
            print("Learning Preferences:")
            for key, value in preferences.items():
                if key != 'updated_at':
                    print(f"  {key}: {value}")
        else:
            console.print("[bold]Learning Preferences:[/bold]")
            for key, value in preferences.items():
                if key != 'updated_at':
                    console.print(f"  [cyan]{key}:[/cyan] {value}")
        return
        
    action = parts[1].strip()
    
    if action == "set":
        key_value = parts[2].split(' ', 1)
        if len(key_value) == 2:
            key, value = key_value
            result = context_manager.execute('set_preference', key=key.strip(), value=value.strip())
            if force_simple_output:
                print(f"Preference set: {key} = {value}")
            else:
                console.print(f"[green]Preference set:[/green] {key} = {value}")

def main():
    global voice_mode
    print_welcome()
    agent = Agent()
    
    while True:
        try:
            if force_simple_output:
                try:
                    user_input = input("You: ")
                except EOFError:
                    # Handle non-interactive environments
                    logger.info("EOF detected - exiting gracefully")
                    break
                except KeyboardInterrupt:
                    logger.info("Keyboard interrupt detected - exiting")
                    break
            else:
                try:
                    user_input = Prompt.ask("[bold green]You[/bold green]")
                except (EOFError, KeyboardInterrupt):
                    # Handle non-interactive environments
                    logger.info("EOF/Keyboard interrupt detected - exiting gracefully")
                    break
            
            if not user_input.strip():
                continue
                
            if user_input.lower() in [":quit", ":exit", "quit", "exit"]:
                if force_simple_output:
                    print("Goodbye!")
                else:
                    console.print("[bold blue]Goodbye![/bold blue]")
                break
                
            if user_input.lower() == ":help":
                print_help()
                continue
                
            if user_input.lower() == ":tools":
                tools_list = ", ".join(agent.tools.keys())
                if force_simple_output:
                    print(f"Available Tools: {tools_list}")
                else:
                    console.print(f"[bold]Available Tools:[/bold] {tools_list}")
                continue
            
            if user_input.lower().startswith(":profile"):
                _handle_profile_command(user_input, agent, force_simple_output, console)
                continue
                
            if user_input.lower().startswith(":topics"):
                _handle_topics_command(agent, force_simple_output, console)
                continue
                
            if user_input.lower().startswith(":preferences"):
                _handle_preferences_command(user_input, agent, force_simple_output, console)
                continue
            
            if user_input.lower() in ["/voicemode", "enable voice mode", "disable voice mode", "voice mode on", "voice mode off"]:
                if user_input.lower() in ["enable voice mode", "voice mode on"]:
                    voice_mode = True
                    status = "enabled"
                elif user_input.lower() in ["disable voice mode", "voice mode off"]:
                    voice_mode = False
                    status = "disabled"
                else:  # Toggle for "/voicemode"
                    voice_mode = not voice_mode
                    status = "enabled" if voice_mode else "disabled"
                
                if force_simple_output:
                    print(f"Voice mode {status}")
                else:
                    console.print(f"Voice mode [bold green]{status}[/bold green]" if voice_mode else f"Voice mode [bold red]{status}[/bold red]")
                continue

            # Process input
            if force_simple_output:
                print("Thinking...")
                intent_data = agent.parse_intent(user_input)
                response = agent.route_and_execute(intent_data)
            else:
                with console.status("[bold yellow]Thinking...[/bold yellow]"):
                    intent_data = agent.parse_intent(user_input)
                    response = agent.route_and_execute(intent_data)
            
            # Display response
            response_text = str(response)
            
            if force_simple_output:
                print("\n" + "=" * 50)
                print("StudBotty:")
                print("-" * 50)
                print(response_text)
                print("=" * 50 + "\n")
            else:
                # Escape response to prevent markup errors from brackets in content (e.g. Mermaid code)
                console.print(Panel(escape(response_text), title="StudBotty", border_style="green"))
            
            # Speak response if voice mode is enabled
            if voice_mode:
                speak(response_text)
            
        except KeyboardInterrupt:
            if force_simple_output:
                print("\nGoodbye!")
            else:
                console.print("\n[bold blue]Goodbye![/bold blue]")
            break
        except Exception as e:
            logger.exception("An error occurred")
            if force_simple_output:
                print(f"Error: {e}")
            else:
                console.print(f"[bold red]Error:[/bold red] {e}")
    


if __name__ == "__main__":
    main()
