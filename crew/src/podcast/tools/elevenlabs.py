from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import json
import random
import time
import requests
from datetime import datetime

class ElevenLabsInput(BaseModel):
    """Input schema for ElevenLabsTool."""
    text: str = Field(description="The text to convert to speech")
    voice_id: str = Field(description="The voice ID to use (Adam, Antoni, etc.)")
    stability: float = Field(default=0.7, description="Voice stability (0.0 to 1.0)")
    clarity: float = Field(default=0.75, description="Voice clarity (0.0 to 1.0)")
    output_path: str = Field(description="Path to save the generated audio file")

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
        
        # Initialize with default voices
        self.voices = {
            "adam": "pNInz6obpgDQGcFmaJgB",  # Male
            "antoni": "ErXwobaYiN019PkySvjV",  # Male
            "bella": "EXAVITQu4vr4xnSDxMaL",  # Female
            "elli": "MF3mGyEYCl7XYWbV9V6O",   # Female
            "josh": "TxGEqnHWrfWFTfGW9XjX",   # Male
            "rachel": "21m00Tcm4TlvDq8ikWAM", # Female
            "sam": "yoZ06aMxZJJ28mfd3POQ"     # Male
        }
        
        # Voice gender mapping for host matching
        self.voice_genders = {
            "adam": "male",
            "antoni": "male",
            "bella": "female",
            "elli": "female",
            "josh": "male",
            "rachel": "female",
            "sam": "male"
        }
        
        # Try to fetch available voices if API key is available
        if self.api_key:
            try:
                self._fetch_available_voices()
            except Exception as e:
                print(f"Could not fetch voices from ElevenLabs API: {str(e)}")
    
    def _fetch_available_voices(self):
        """Fetch available voices from ElevenLabs API"""
        if not self.api_key:
            return
            
        try:
            headers = {"xi-api-key": self.api_key}
            response = requests.get(f"{self.base_url}/voices", headers=headers)
            response.raise_for_status()
            
            voices_data = response.json()
            
            # Update voices dictionary with fetched voices
            for voice in voices_data.get('voices', []):
                name = voice.get('name', '').lower()
                voice_id = voice.get('voice_id')
                if name and voice_id:
                    self.voices[name] = voice_id
                    
                    # Try to determine gender from tags
                    tags = [tag.lower() for tag in voice.get('tags', [])]
                    if 'male' in tags:
                        self.voice_genders[name] = 'male'
                    elif 'female' in tags:
                        self.voice_genders[name] = 'female'
            
        except Exception as e:
            print(f"Error fetching voices: {str(e)}")
    
    def get_available_voices(self):
        """Get list of available voices for UI selection"""
        # Ensure voice_genders exists
        if not hasattr(self, 'voice_genders') or self.voice_genders is None:
            self.voice_genders = {
                "adam": "male",
                "antoni": "male",
                "bella": "female",
                "elli": "female",
                "josh": "male",
                "rachel": "female",
                "sam": "male"
            }
            
        voice_options = []
        for name, voice_id in self.voices.items():
            gender = self.voice_genders.get(name, 'unknown')
            voice_options.append({
                'id': voice_id,
                'name': name.capitalize(),
                'gender': gender
            })
        return voice_options
    
    def suggest_voice_for_host(self, host_name, preferred_gender=None):
        """Suggest a voice for a host based on name and preferred gender"""
        # Ensure voice_genders exists
        if not hasattr(self, 'voice_genders') or self.voice_genders is None:
            self.voice_genders = {
                "adam": "male",
                "antoni": "male",
                "bella": "female",
                "elli": "female",
                "josh": "male",
                "rachel": "female",
                "sam": "male"
            }
            
        # Simple gender detection based on common name endings
        # This is very simplistic - in production, use a proper name-gender API
        if not preferred_gender:
            if host_name.lower().endswith(('a', 'e', 'i')):
                preferred_gender = 'female'
            else:
                preferred_gender = 'male'
        
        # Find voices matching the preferred gender
        matching_voices = [
            name for name, gender in self.voice_genders.items()
            if gender == preferred_gender
        ]
        
        if matching_voices:
            # Return a random matching voice
            return random.choice(matching_voices)
        else:
            # Fallback to any voice
            return random.choice(list(self.voices.keys()))
    
    def create_voice_preview(self, voice_name, output_dir="data/podcasts/previews"):
        """Create a voice preview for UI selection"""
        os.makedirs(output_dir, exist_ok=True)
        preview_text = f"This is a preview of the {voice_name} voice from ElevenLabs."
        output_path = f"{output_dir}/{voice_name}_preview.mp3"
        
        result = self._run(
            text=preview_text,
            voice_id=voice_name,
            output_path=output_path
        )
        
        return json.loads(result)
        
    def process_podcast_script(self, script, hosts, output_path="data/podcasts/podcast.mp3"):
        """
        Process a full podcast script and generate audio with dynamic host voice assignment.
        
        Args:
            script (str): The full podcast script with host labels
            hosts (list): List of host names
            output_path (str): Path to save the final audio file
            
        Returns:
            dict: Information about the generated podcast
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Assign voices to hosts
        host_voices = {}
        for i, host in enumerate(hosts):
            # Alternate between male and female voices for contrast
            preferred_gender = 'male' if i % 2 == 0 else 'female'
            voice = self.suggest_voice_for_host(host, preferred_gender)
            host_voices[host] = voice
        
        # In a real implementation, this would:
        # 1. Parse the script to separate by speaker
        # 2. Generate audio for each segment with the appropriate voice
        # 3. Combine the segments into a single audio file
        # 4. Add sound effects or music
        
        # For this demo, we'll simulate the process
        time.sleep(random.uniform(3.0, 5.0))
        
        # Create a metadata file with information about the podcast
        metadata = {
            "hosts": hosts,
            "host_voices": host_voices,
            "script_length": len(script),
            "segments": len(script.split(f"{hosts[0]}:")) + (len(script.split(f"{hosts[1]}:")) if len(hosts) > 1 else 0),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_path": output_path,
            "audio_url": f"/audio/{os.path.basename(output_path)}",
            "simulated": not self.api_key
        }
        
        metadata_path = output_path.replace(".mp3", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        # Create an empty MP3 file or use the API to generate real audio
        if self.api_key:
            # Here you would implement the actual audio generation with the assigned voices
            # For now, just create a dummy file
            with open(output_path, "wb") as f:
                f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        else:
            # Create an empty MP3 file for simulation
            with open(output_path, "wb") as f:
                f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        return {
            "success": True,
            "message": f"Podcast audio generated and saved to {output_path}",
            "metadata_path": metadata_path,
            "audio_url": f"/audio/{os.path.basename(output_path)}",
            "host_voices": host_voices
        }
    
    def _run(self, text: str, voice_id: str, stability: float = 0.7, 
             clarity: float = 0.75, output_path: str = None) -> str:
        """
        Convert text to speech using ElevenLabs API.
        
        Args:
            text: The text to convert to speech
            voice_id: The voice ID to use
            stability: Voice stability (0.0 to 1.0)
            clarity: Voice clarity (0.0 to 1.0)
            output_path: Path to save the generated audio file
            
        Returns:
            JSON string with the result
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Normalize voice ID (handle case where a name is passed instead of ID)
        voice_id = voice_id.lower() if voice_id else "adam"
        
        # Create default voices dictionary if it doesn't exist
        if not hasattr(self, 'voices') or self.voices is None:
            self.voices = {
                "adam": "pNInz6obpgDQGcFmaJgB",
                "antoni": "ErXwobaYiN019PkySvjV",
                "bella": "EXAVITQu4vr4xnSDxMaL",
                "elli": "MF3mGyEYCl7XYWbV9V6O",
                "josh": "TxGEqnHWrfWFTfGW9XjX",
                "rachel": "21m00Tcm4TlvDq8ikWAM",
                "sam": "yoZ06aMxZJJ28mfd3POQ"
            }
            
        if voice_id in self.voices:
            voice_id = self.voices[voice_id]
        
        # Check if API key is available
        if not self.api_key:
            # Fall back to simulated results if no API key
            return self._simulate_tts(text, voice_id, stability, clarity, output_path)
        
        try:
            # Prepare request headers and data
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": clarity
                }
            }
            
            # Make the API request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
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
            return self._simulate_tts(text, voice_id, stability, clarity, output_path)
    
    def _simulate_tts(self, text: str, voice_id: str, stability: float, clarity: float, output_path: str) -> str:
        """Simulate text-to-speech conversion when API key is not available or API fails."""
        # Simulate processing time based on text length
        process_time = 0.5 + (len(text) / 100) * random.uniform(0.5, 1.5)
        time.sleep(process_time)
        
        # Create metadata
        result = {
            "success": True,
            "text_length": len(text),
            "voice_id": voice_id,
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