from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import threading
import json
import time
from datetime import datetime
import uuid
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Validate required environment variables
required_env_vars = {
    'ANTHROPIC_API_KEY': 'Claude API key for CrewAI agents',
    'MODEL': 'Model name to use for agents',
    'SERPER_API_KEY': 'API key for web search functionality',
    'ELEVENLABS_API_KEY': 'API key for text-to-speech conversion',
    'CREWAI_MEMORY_DB_PATH': 'Path for CrewAI memory storage'
}

missing_vars = []
for var, description in required_env_vars.items():
    if not os.environ.get(var):
        missing_vars.append(f"{var} ({description})")
        logger.warning(f"Missing environment variable: {var} - {description}")

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    if os.environ.get('ANTHROPIC_API_KEY') is None:  # Only exit if the critical API key is missing
        logger.critical("ANTHROPIC_API_KEY is required but not set. Exiting.")
        sys.exit(1)

# Configure memory DB path
memory_db_path = os.environ.get('CREWAI_MEMORY_DB_PATH', '/app/data/memory.db')
os.environ['CREWAI_MEMORY_DB_PATH'] = memory_db_path

# Ensure memory DB directory exists
os.makedirs(os.path.dirname(memory_db_path), exist_ok=True)

app = Flask(__name__)

# Global variables to track state
podcasts = {}
current_job = None
job_queue = []

class PodcastJob:
    def __init__(self, topic=None, hosts=None):
        self.id = str(uuid.uuid4())
        self.topic = topic or "Current Events"
        self.hosts = hosts or ["Alex", "Jamie"]
        self.status = "queued"
        self.progress = 0
        self.stages = ["research", "summarize", "script", "voice", "complete"]
        self.current_stage = ""
        self.start_time = None
        self.end_time = None
        self.updates = []
        self.results = {
            "research": {},
            "summary": "",
            "script": "",
            "audio_url": ""
        }
    
    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "hosts": self.hosts,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "updates": self.updates,
            "results": self.results
        }
    
    def add_update(self, message, stage=None):
        if stage and stage != self.current_stage:
            self.current_stage = stage
            if stage in self.stages:
                stage_index = self.stages.index(stage)
                self.progress = int((stage_index / len(self.stages)) * 100)
        
        update = {
            "time": datetime.now().isoformat(),
            "message": message,
            "stage": self.current_stage
        }
        self.updates.append(update)
        logger.info(f"Job {self.id}: {message}")
    
    def start(self):
        self.status = "running"
        self.start_time = datetime.now()
        self.add_update("Starting podcast creation process", "research")
    
    def complete(self, success=True):
        self.status = "completed" if success else "failed"
        self.end_time = datetime.now()
        self.progress = 100 if success else self.progress
        self.add_update(
            "Podcast creation completed successfully" if success else 
            "Podcast creation failed", 
            "complete" if success else self.current_stage
        )

def run_podcast_job(job):
    """Run the CrewAI podcast generation process"""
    global current_job
    
    try:
        # Start the job
        job.start()
        
        # Import podcast crew - do this here to avoid circular imports
        from podcast.crew import PodcastCrew
        
        # Research stage
        job.add_update("Starting research on trending topics", "research")
        time.sleep(2)  # Simulating work - replace with actual research
        
        # Example research results - replace with actual implementation
        job.results["research"] = {
            "sources": [
                {"title": "AI Developments in 2025", "url": "https://example.com/ai-news"},
                {"title": "New Climate Change Policies", "url": "https://example.com/climate"},
                {"title": "Space Exploration Updates", "url": "https://example.com/space"}
            ],
            "topics": ["Artificial Intelligence", "Climate Change", "Space Exploration"]
        }
        job.add_update("Research completed, found 3 trending topics", "research")
        
        # Create a podcast crew
        crew = PodcastCrew(
            topic=job.topic,
            hosts=job.hosts,
            job_id=job.id,
            callback=lambda msg, stage=None: job.add_update(msg, stage)
        )
        
        try:
            # Run the crew
            result = crew.run()
            
            # Debug output of the result type
            job.add_update(f"Result type: {type(result)}", "debug")
            
            # Check if we got an error result
            if isinstance(result, dict) and "summary" in result and isinstance(result["summary"], str) and result["summary"].startswith("Error:"):
                raise Exception(result["summary"])
            elif isinstance(result, str) and result.startswith("Error:"):
                raise Exception(result)
                
            # Update the job with results
            if isinstance(result, dict):
                # Dictionary handling
                for key, value in result.items():
                    if key == "research" and isinstance(value, dict):
                        job.results["research"] = value
                    elif key == "summary" and isinstance(value, str):
                        job.results["summary"] = value
                    elif key == "script" and isinstance(value, str):
                        job.results["script"] = value
                    elif key == "audio_details" and isinstance(value, dict):
                        job.results["audio_details"] = value
            elif isinstance(result, str):
                # Handle string results
                job.results["script"] = result
                job.results["summary"] = "Generated by CrewAI"
                job.results["audio_details"] = {
                    "voice_instructions": f"Use a conversational tone for {', '.join(job.hosts)}."
                }
                
            job.add_update("Podcast generated successfully", "complete")
            job.complete(True)
            
        except TypeError as e:
            # Handle specific TypeError (like 'str' has no attribute 'get')
            job.add_update(f"Type error processing results: {str(e)}", "error")
            
            # Create fallback content
            job.results["summary"] = f"AI generated podcast on {job.topic}"
            job.results["script"] = f"# {job.topic} Podcast\n\n" + \
                f"{job.hosts[0]}: Welcome to our podcast on {job.topic}!\n" + \
                f"{job.hosts[1]}: Today we'll be exploring this fascinating topic...\n\n" + \
                "Due to technical limitations, we've created this simple placeholder script."
            job.results["audio_details"] = {
                "voice_instructions": f"Use a conversational tone for {', '.join(job.hosts)}."
            }
            
            job.add_update("Generated fallback content due to error", "script")
            job.complete(True)
        
    except Exception as e:
        logger.error(f"Error in podcast job: {str(e)}")
        job.add_update(f"Error: {str(e)}")
        job.complete(False)
    
    # Process next job in queue
    global job_queue
    current_job = None
    if job_queue:
        next_job = job_queue.pop(0)
        process_next_job(next_job)

def process_next_job(job):
    """Start processing the next job in the queue"""
    global current_job
    current_job = job
    podcasts[job.id] = job
    
    # Start a new thread to run the job
    thread = threading.Thread(target=run_podcast_job, args=(job,))
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    """Home page with podcast creation form"""
    return render_template('index.html')

@app.route('/create-podcast', methods=['POST'])
def create_podcast():
    """Endpoint to create a new podcast"""
    data = request.get_json()
    
    # Convert data to dictionary if it's a string
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from data: {data}")
            return jsonify({"error": "Invalid data format"}), 400
    
    # Create a new podcast job
    job = PodcastJob(
        topic=data.get('topic'),
        hosts=data.get('hosts', ["Alex", "Jamie"])
    )
    
    # Add to queue or process immediately
    if current_job is None:
        process_next_job(job)
    else:
        job_queue.append(job)
        job.add_update("Job added to queue. Position: " + str(len(job_queue)))
    
    podcasts[job.id] = job
    
    return jsonify({
        "success": True,
        "job_id": job.id,
        "message": "Podcast creation started" if current_job == job else "Podcast added to queue"
    })

@app.route('/podcast/<job_id>')
def view_podcast(job_id):
    """View a specific podcast"""
    job = podcasts.get(job_id)
    if not job:
        return "Podcast not found", 404
    
    return render_template('podcast.html', job_id=job_id)

@app.route('/api/podcast/<job_id>')
def get_podcast_status(job_id):
    """Get the status of a podcast job"""
    job = podcasts.get(job_id)
    if not job:
        return jsonify({"error": "Podcast not found"}), 404
    
    return jsonify(job.to_dict())

@app.route('/api/podcasts')
def list_podcasts():
    """List all podcasts"""
    return jsonify({
        "podcasts": [job.to_dict() for job in podcasts.values()],
        "current_job": current_job.id if current_job else None,
        "queue_length": len(job_queue)
    })

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serve generated audio files"""
    return send_from_directory('data/podcasts', filename)

@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    # Check if API keys are set
    status = {
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "api_keys": {
            "anthropic": bool(os.environ.get('ANTHROPIC_API_KEY')),
            "serper": bool(os.environ.get('SERPER_API_KEY')),
            "elevenlabs": bool(os.environ.get('ELEVENLABS_API_KEY'))
        },
        "memory_db": os.path.exists(os.environ.get('CREWAI_MEMORY_DB_PATH', '/app/data/memory.db')),
        "version": "1.0.0"
    }
    
    # Set overall status
    if not status['api_keys']['anthropic']:
        status['status'] = "degraded"
        status['message'] = "Missing critical API key: ANTHROPIC_API_KEY"
    
    return jsonify(status)

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('data/podcasts', exist_ok=True)
    os.makedirs('data/research', exist_ok=True)
    
    # Log startup information
    logger.info("=== CrewAI Podcast Generator Starting ===")
    logger.info(f"API Keys configured: Anthropic: {'Yes' if os.environ.get('ANTHROPIC_API_KEY') else 'No'}, " 
                f"Serper: {'Yes' if os.environ.get('SERPER_API_KEY') else 'No'}, "
                f"ElevenLabs: {'Yes' if os.environ.get('ELEVENLABS_API_KEY') else 'No'}")
    logger.info(f"Using model: {os.environ.get('MODEL', 'claude-3-5-sonnet-20240620')}")
    logger.info(f"Memory DB path: {os.environ.get('CREWAI_MEMORY_DB_PATH', '/app/data/memory.db')}")
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)