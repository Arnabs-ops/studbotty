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
        print("Type :help for commands.")
        print("=" * 30)
    else:
        console.print(Panel.fit(
            "[bold blue]Welcome to StudBotty![/bold blue]\n"
            "Your AI Study Companion.\n"
            "Type [bold cyan]:help[/bold cyan] for commands.",
            title="StudBotty",
            border_style="blue"
        ))

def print_help():
    if force_simple_output:
        help_text = """
Commands:
- :help       Show this help message
- :quit       Exit the application
- :tools      List available tools
- :history    Show session history (not implemented yet)
- :profile    Manage user profile (see usage below)
- :topics     Show important topics
- :preferences Manage learning preferences
- enable voice mode  Enable voice mode (TTS)
- disable voice mode  Disable voice mode
- voice mode on/off   Turn voice mode on or off

Profile Commands:
- :profile set key value    Set profile field
- :profile get key          Get profile field
- :profile show             Show all profile data

Examples:
- "Explain photosynthesis"
- "Solve 2 + 2"
- "Quiz me on python"
- "Visualize a binary tree"
- "Speak hello world" or "TTS hello world"
- "Say this text will be spoken aloud"
- "enable voice mode" - Simple voice mode activation
        """
        print(help_text)
    else:
        help_text = """
    [bold]Commands:[/bold]
    - [cyan]:help[/cyan]       Show this help message
    - [cyan]:quit[/cyan]       Exit the application
    - [cyan]:tools[/cyan]      List available tools
    - [cyan]:history[/cyan]    Show session history (not implemented yet)
    - [cyan]:profile[/cyan]    Manage user profile (see usage below)
    - [cyan]:topics[/cyan]     Show important topics
    - [cyan]:preferences[/cyan] Manage learning preferences
    - [cyan]enable voice mode[/cyan]  Enable voice mode (TTS)
    - [cyan]disable voice mode[/cyan] Disable voice mode
    - [cyan]voice mode on/off[/cyan]   Turn voice mode on or off
    
    [bold]Profile Commands:[/bold]
    - [cyan]:profile set key value[/cyan]    Set profile field
    - [cyan]:profile get key[/cyan]          Get profile field
    - [cyan]:profile show[/cyan]             Show all profile data
    
    [bold]Examples:[/bold]
    - "Explain photosynthesis"
    - "Solve 2 + 2"
    - "Quiz me on python"
    - "Visualize a binary tree"
    - "Speak hello world" or "TTS hello world"
    - "Say this text will be spoken aloud"
    - "enable voice mode" - Simple voice mode activation
    """
        console.print(help_text, markup=True)

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
