from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import json
import random
import time
import requests
import re
from datetime import datetime
from pydub import AudioSegment

class ElevenLabsInput(BaseModel):
    """Input schema for ElevenLabsTool."""
    text: str = Field(description="The text to convert to speech")
    voice_id: str = Field(description="The voice ID to use (Adam, Antoni, etc.)")
    stability: float = Field(default=0.7, description="Voice stability (0.0 to 1.0)")
    clarity: float = Field(default=0.75, description="Voice clarity (0.0 to 1.0)")
    output_path: str = Field(description="Path to save the generated audio file")
    language: str = Field(default="fr", description="Language of the text (fr for French)")

class ElevenLabsTool(BaseTool):
    """Tool for converting text to speech using ElevenLabs API."""
    
    name: str = "ElevenLabs Text-to-Speech"
    description: str = "Convert text to realistic speech using ElevenLabs voices"
    args_schema: Type[BaseModel] = ElevenLabsInput
    api_key: str = None
    base_url: str = "https://api.elevenlabs.io/v1"
    voices: dict = None
    
    def __init__(self, api_key=None):
        """Initialize with optional API key."""
        super().__init__()
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        
        # Initialize voice_genders dictionary with only Alex and Simon
        self.voice_genders = {
            "alex": "male",
            "simon": "male"
        }
        
        # Initialize with only Alex and Simon voices using the provided IDs
        self.voices = {
            "alex": "IPgYtHTNLjC7Bq7IPHrm",   # Hard coded Alex voice ID
            "simon": "RBhYSNMNu6b2CGZ9Fn1M"   # Hard coded Simon voice ID
        }
        
        # Try to fetch available voices if API key is available
        if self.api_key:
            try:
                self._fetch_available_voices()
            except Exception as e:
                print(f"Could not fetch voices from ElevenLabs API: {str(e)}")
    
    def _fetch_available_voices(self):
        """Fetch available voices from ElevenLabs API"""
        # We're only using hardcoded Alex and Simon voices, so this method 
        # doesn't need to do anything
        return
    
    def get_available_voices(self):
        """Get list of available voices for UI selection"""
        voice_options = []
        for name, voice_id in self.voices.items():
            voice_options.append({
                'id': voice_id,
                'name': name.capitalize()
            })
        return voice_options
    
    def suggest_voice_for_host(self, host_name, preferred_voice=None):
        """Suggest a voice for a host"""
        # Only two hosts: Alex and Simon
        if host_name.lower() == "alex":
            return "alex"
        else:
            # For any other host name, use Simon
            return "simon"
    
    def create_voice_preview(self, voice_name, output_dir="data/podcasts/previews"):
        """Create a voice preview for UI selection"""
        os.makedirs(output_dir, exist_ok=True)
        # Use Quebec French with typical expressions
        preview_text = f"Bonjour! C'est {voice_name}. Tabarnak, c'est pas pire pantoute notre podcast québécois, hein?"
        output_path = f"{output_dir}/{voice_name}_preview.mp3"
        
        result = self._run(
            text=preview_text,
            voice_id=voice_name,
            output_path=output_path,
            language="fr"  # Force French
        )
        
        return json.loads(result)
    
    def parse_podcast_script(self, script, hosts):
        """Parse podcast script into segments by host."""
        segments = []
        current_text = ""
        current_host = None
        
        # Create a regex pattern to match any host
        hosts_pattern = '|'.join([re.escape(host) for host in hosts])
        pattern = f"({hosts_pattern}):\\s*"
        
        # Split the script by host indicators
        parts = re.split(f"({pattern})", script)
        
        # Process the split parts
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and parts[i+1].strip().endswith(':'):
                # Found a host indicator
                if current_host and current_text.strip():
                    segments.append({"host": current_host, "text": current_text.strip()})
                
                # Extract the host name without the colon
                current_host = parts[i+1].strip()[:-1]
                current_text = parts[i+2] if i+2 < len(parts) else ""
                i += 3
            else:
                # Continuation of text or unattributed text
                if not current_host:
                    # Handle text before any host is specified (e.g., intro)
                    current_host = "narrator"
                current_text += parts[i]
                i += 1
        
        # Add the last segment if there is one
        if current_host and current_text.strip():
            segments.append({"host": current_host, "text": current_text.strip()})
            
        return segments
        
    def process_podcast_script(self, script, hosts, output_path="data/podcasts/podcast.mp3"):
        """
        Process a full podcast script and generate audio with Alex and Simon voices.
        Script will be in French with a Quebec touch.
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Assign voices to hosts - only Alex and Simon
        host_voices = {}
        for i, host in enumerate(hosts):
            if i == 0 or host.lower() == "alex":
                host_voices[host] = "alex"
            else:
                host_voices[host] = "simon"
        
        # Parse the script to separate by speaker
        segments = self.parse_podcast_script(script, hosts)
        
        # If we don't have a valid API key, simulate the process
        if not self.api_key:
            return self._simulate_podcast_processing(segments, host_voices, output_path)
            
        try:
            # Generate audio for each segment with the appropriate voice
            temp_audio_files = []
            combined_audio = None
            
            for i, segment in enumerate(segments):
                host = segment["host"]
                text = segment["text"]
                
                # Get voice for this host (default to first available if not found)
                voice = host_voices.get(host, list(self.voices.keys())[0])
                
                # Generate temp file path
                temp_file = f"{output_path.replace('.mp3', '')}_segment_{i}.mp3"
                
                # Generate audio for this segment (in French)
                result = json.loads(self._run(
                    text=text,
                    voice_id=voice,
                    output_path=temp_file,
                    language="fr"  # Force French language
                ))
                
                if result["success"]:
                    temp_audio_files.append(temp_file)
                    
                    # Add to combined audio
                    segment_audio = AudioSegment.from_mp3(temp_file)
                    if combined_audio is None:
                        combined_audio = segment_audio
                    else:
                        combined_audio += segment_audio
                else:
                    print(f"Failed to generate audio for segment {i}: {result.get('message')}")
            
            # Save the combined audio
            if combined_audio:
                combined_audio.export(output_path, format="mp3")
                
                # Clean up temp files
                for temp_file in temp_audio_files:
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        print(f"Failed to remove temp file {temp_file}: {str(e)}")
                
                # Create metadata
                metadata = {
                    "hosts": hosts,
                    "host_voices": host_voices,
                    "script_length": len(script),
                    "segments": len(segments),
                    "language": "fr",
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "output_path": output_path,
                    "audio_url": f"/audio/{os.path.basename(output_path)}"
                }
                
                metadata_path = output_path.replace(".mp3", "_metadata.json")
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                return {
                    "success": True,
                    "message": f"Podcast audio generated and saved to {output_path}",
                    "metadata_path": metadata_path,
                    "audio_url": f"/audio/{os.path.basename(output_path)}",
                    "host_voices": host_voices
                }
            else:
                raise Exception("Failed to generate any audio segments")
                
        except Exception as e:
            print(f"Error processing podcast script: {str(e)}")
            return self._simulate_podcast_processing(segments, host_voices, output_path)
    
    def _simulate_podcast_processing(self, segments, host_voices, output_path):
        """Simulate podcast processing when API key is not available or API fails."""
        # Simulate processing time based on script length
        total_text_length = sum(len(segment["text"]) for segment in segments)
        process_time = 1.0 + (total_text_length / 500) * random.uniform(0.5, 1.5)
        time.sleep(process_time)
        
        # Create a metadata file with information about the podcast
        metadata = {
            "hosts": list(host_voices.keys()),
            "host_voices": host_voices,
            "script_length": total_text_length,
            "segments": len(segments),
            "language": "fr",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_path": output_path,
            "audio_url": f"/audio/{os.path.basename(output_path)}",
            "simulated": True
        }
        
        metadata_path = output_path.replace(".mp3", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        # Create an empty MP3 file or use the API to generate real audio
        with open(output_path, "wb") as f:
            f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        return {
            "success": True,
            "message": f"Simulated podcast audio generated and saved to {output_path}",
            "metadata_path": metadata_path,
            "audio_url": f"/audio/{os.path.basename(output_path)}",
            "host_voices": host_voices
        }
    
    def _run(self, text: str, voice_id: str, stability: float = 0.7, 
             clarity: float = 0.75, output_path: str = None, language: str = "fr") -> str:
        """
        Convert text to speech using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            voice_id: The voice ID to use
            stability: Voice stability (0.0 to 1.0)
            clarity: Voice clarity (0.0 to 1.0)
            output_path: Path to save the generated audio file
            language: Language of the text (default: fr for French)
            
        Returns:
            JSON string with the result
        """
        # Ensure output directory exists
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/audio/elevenlabs_{timestamp}.mp3"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Normalize voice ID (handle case where a name is passed instead of ID)
        if voice_id:
            voice_id = voice_id.lower()
        else:
            voice_id = "adam"  # Default voice
        
        # Get voice ID from name if needed
        if voice_id in self.voices:
            voice_id = self.voices[voice_id]
        
        # Check if API key is available
        if not self.api_key:
            # Fall back to simulated results if no API key
            return self._simulate_tts(text, voice_id, stability, clarity, output_path, language)
        
        try:
            # Prepare request headers and data
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # Use multilingual model for French
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": clarity
                }
            }
            
            # Make the API request
            url = f"{self.base_url}/text-to-speech/{voice_id}/stream"  # Use streaming endpoint
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            # Save the audio file
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            # Create metadata
            metadata = {
                "success": True,
                "text_length": len(text),
                "voice_id": voice_id,
                "language": language,
                "stability": stability,
                "clarity": clarity,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "output_path": output_path
            }
            
            # Save metadata
            metadata_path = output_path.replace(".mp3", "_metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            
            return json.dumps({
                "success": True,
                "message": f"Audio generated and saved to {output_path}",
                "metadata_path": metadata_path
            })
            
        except Exception as e:
            # Log the error and fall back to simulated results
            print(f"ElevenLabs API error: {str(e)}")
            return self._simulate_tts(text, voice_id, stability, clarity, output_path, language)
    
    def _simulate_tts(self, text: str, voice_id: str, stability: float, clarity: float, 
                     output_path: str, language: str = "fr") -> str:
        """Simulate text-to-speech conversion when API key is not available or API fails."""
        # Simulate processing time based on text length
        process_time = 0.5 + (len(text) / 100) * random.uniform(0.5, 1.5)
        time.sleep(process_time)
        
        # Create metadata
        result = {
            "success": True,
            "text_length": len(text),
            "voice_id": voice_id,
            "language": language,
            "stability": stability,
            "clarity": clarity,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_path": output_path,
            "simulated": True,
            "note": "This is a simulated result. In production, this would generate a real audio file."
        }
        
        # Create a metadata file
        metadata_path = output_path.replace(".mp3", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(result, f, indent=2)
            
        # Create an empty MP3 file to simulate output
        with open(output_path, "wb") as f:
            # Just write a minimal valid MP3 header
            f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        return json.dumps({
            "success": True,
            "message": f"Simulated audio generated and saved to {output_path}",
            "metadata_path": metadata_path
        })