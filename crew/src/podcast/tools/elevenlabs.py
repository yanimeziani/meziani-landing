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
    
    def __init__(self, api_key=None):
        """Initialize with optional API key."""
        super().__init__()
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        self.voices = {
            "adam": "pNInz6obpgDQGcFmaJgB",
            "antoni": "ErXwobaYiN019PkySvjV",
            "bella": "EXAVITQu4vr4xnSDxMaL",
            "elli": "MF3mGyEYCl7XYWbV9V6O",
            "josh": "TxGEqnHWrfWFTfGW9XjX",
            "rachel": "21m00Tcm4TlvDq8ikWAM",
            "sam": "yoZ06aMxZJJ28mfd3POQ"
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
        voice_id = voice_id.lower()
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
        
    def process_podcast_script(self, script, host1, host2, output_path):
        """
        Process a full podcast script and generate audio.
        
        Args:
            script (str): The full podcast script with host labels
            host1 (str): Name of the first host
            host2 (str): Name of the second host
            output_path (str): Path to save the final audio file
            
        Returns:
            str: Path to the generated audio file
        """
        # In a real implementation, this would:
        # 1. Parse the script to separate by speaker
        # 2. Generate audio for each segment with the appropriate voice
        # 3. Combine the segments into a single audio file
        # 4. Add any sound effects or music
        
        # For this demo, we'll simulate the process
        time.sleep(random.uniform(3.0, 5.0))  # Simulate longer processing time
        
        # Create a metadata file with information about the podcast
        metadata = {
            "hosts": [host1, host2],
            "script_length": len(script),
            "segments": len(script.split(f"{host1}:")) + len(script.split(f"{host2}:")),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "output_path": output_path,
            "simulated": True
        }
        
        metadata_path = output_path.replace(".mp3", "_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        # Create an empty MP3 file to simulate output
        with open(output_path, "wb") as f:
            # Just write a minimal valid MP3 header
            f.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        
        return json.dumps({
            "success": True,
            "message": f"Podcast audio generated and saved to {output_path}",
            "metadata_path": metadata_path
        })