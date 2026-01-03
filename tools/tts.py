from typing import Any, Dict
from tools.base import Tool
import re
import os
import tempfile
import subprocess
import platform
from config import config

class TTSTool(Tool):
    def __init__(self):
        super().__init__(name="tts", description="Powerful and efficient Text-to-Speech tool.")

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to convert to speech"},
                "voice": {
                    "type": "string", 
                    "enum": ["male", "female", "natural", "robotic"], 
                    "default": "natural",
                    "description": "Voice type"
                },
                "speed": {"type": "number", "default": 1.0, "minimum": 0.5, "maximum": 2.0, "description": "Speech speed multiplier"},
                "volume": {"type": "number", "default": 1.0, "minimum": 0.1, "maximum": 1.0, "description": "Volume level"},
                "save_to_file": {"type": "boolean", "default": False, "description": "Save output to file"},
                "filename": {"type": "string", "description": "Output filename (if save_to_file is true)"},
                "format": {"type": "string", "enum": ["mp3", "wav", "ogg"], "default": "mp3", "description": "Audio format"}
            },
            "required": ["text"]
        }

    def _remove_emojis(self, text: str) -> str:
        """Remove emojis from text using optimized regex"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"  # chinese char
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
            "\u3030"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better TTS performance"""
        # Remove emojis
        text = self._remove_emojis(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Replace common abbreviations for better pronunciation
        replacements = {
            "i.e.": "that is",
            "e.g.": "for example", 
            "etc.": "et cetera",
            "vs.": "versus",
            "Mr.": "Mister",
            "Mrs.": "Missus",
            "Dr.": "Doctor",
            "Prof.": "Professor",
            "&": "and",
            "@": "at",
            "#": "hashtag"
        }
        
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
            
        return text

    def _get_system_voices(self):
        """Get available system voices efficiently"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            return voices
        except:
            return []

    def _optimized_pyttsx3(self, text: str, voice_type: str = "natural",
                           speed: float = 1.0, volume: float = 1.0,
                           save_to_file: bool = False, filename: str = None,
                           format: str = "mp3") -> str:
        """Highly optimized pyttsx3 TTS with performance enhancements"""
        try:
            # Suppress comtypes logging to clean up output
            import logging
            import pyttsx3
            
            # Disable comtypes and pyttsx3 debug logging
            logging.getLogger('comtypes').setLevel(logging.WARNING)
            logging.getLogger('pyttsx3').setLevel(logging.WARNING)
            
            # Clean and prepare text
            clean_text = self._clean_text(text)
            
            if not clean_text:
                return "❌ No valid text to speak"
                
            # Initialize engine with optimizations
            engine = pyttsx3.init()
            
            # Apply performance settings
            engine.setProperty('rate', int(180 * speed))  # Optimized base rate
            engine.setProperty('volume', min(max(volume, 0.1), 1.0))
            
            # Select voice based on type
            voices = self._get_system_voices()
            
            if voices:
                if voice_type == "female" and len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                elif voice_type == "male" and len(voices) > 0:
                    engine.setProperty('voice', voices[0].id)
                elif voice_type == "robotic" and len(voices) > 2:
                    engine.setProperty('voice', voices[2].id)
                else:
                    # Use natural voice (usually voices[1] if available)
                    if len(voices) > 1:
                        engine.setProperty('voice', voices[1].id)
            
            if save_to_file:
                # Ensure filename has correct extension
                if not filename:
                    filename = f"tts_output.{format}"
                elif not filename.endswith(f'.{format}'):
                    filename += f'.{format}'
                
                # Save to file with error handling
                try:
                    engine.save_to_file(clean_text, filename)
                    engine.runAndWait()
                    return f"🎵 Speech saved to {filename} ({len(clean_text)} chars, {speed}x speed)"
                except Exception as e:
                    return f"❌ Failed to save file: {str(e)}"
            else:
                # Direct speech with performance monitoring
                engine.say(clean_text)
                engine.runAndWait()
                return f"🎵 Speech completed ({len(clean_text)} chars, {speed}x speed, {volume}x volume)"
                
        except ImportError:
            return "❌ pyttsx3 not installed. Install with: pip install pyttsx3"
        except Exception as e:
            return f"❌ TTS error: {str(e)}"

    def _system_tts_fallback(self, text: str):
        """Fallback to system TTS commands for maximum compatibility"""
        try:
            clean_text = self._clean_text(text)
            
            if platform.system() == "Windows":
                # Windows: Use powershell speech
                import subprocess
                cmd = f'powershell -c "Add-Type -AssemblyName System.speech; $speech = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speech.Speak(\"{clean_text}\")"'
                subprocess.run(cmd, shell=True, check=True)
                return "🎵 Windows system speech completed"
                
            elif platform.system() == "Darwin":
                # macOS: Use say command
                subprocess.run(["say", clean_text], check=True)
                return "🎵 macOS system speech completed"
                
            elif platform.system() == "Linux":
                # Linux: Try various TTS commands
                try:
                    subprocess.run(["spd-say", clean_text], check=True)
                    return "🎵 Linux speech-dispatcher completed"
                except:
                    try:
                        subprocess.run(["espeak", clean_text], check=True)
                        return "🎵 Linux espeak completed"
                    except:
                        try:
                            subprocess.run(["festival", "--tts", clean_text], check=True)
                            return "🎵 Linux festival completed"
                        except:
                            return "❌ No compatible Linux TTS found"
            else:
                return "❌ Unsupported platform for system TTS"
                
        except Exception as e:
            return f"❌ System TTS error: {str(e)}"

    def _batch_processing(self, text: str) -> str:
        """Process large text efficiently using batch processing"""
        if len(text) > 1000:  # For long texts
            sentences = re.split(r'(?<=[.!?])\s+', text)
            results = []
            
            for i, sentence in enumerate(sentences):
                if len(sentence) > 10:  # Skip very short fragments
                    result = self._optimized_pyttsx3(sentence)
                    results.append(f"Part {i+1}: {result}")
            
            return "🎵 Batch processing completed:\n" + "\n".join(results)
        else:
            return self._optimized_pyttsx3(text)

    def execute(self, text: str, voice: str = "natural", speed: float = 1.0, 
                volume: float = 1.0, save_to_file: bool = False, 
                filename: str = None, format: str = "mp3") -> str:
        """Execute powerful TTS with optimizations"""
        
        # Validate inputs
        if not text or not text.strip():
            return "❌ No text provided for TTS"
            
        # Clamp values to valid ranges
        speed = max(0.5, min(2.0, speed))
        volume = max(0.1, min(1.0, volume))
        
        # Try optimized pyttsx3 first
        result = self._optimized_pyttsx3(text, voice, speed, volume, save_to_file, filename, format)
        
        # If pyttsx3 fails, try system fallback
        if "not installed" in result or "error" in result.lower():
            fallback_result = self._system_tts_fallback(text)
            if "completed" in fallback_result:
                return fallback_result
            else:
                return result + "\n" + fallback_result
                
        return result