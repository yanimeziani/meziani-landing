from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import threading
import json
import time
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        
        # Run the crew
        result = crew.run()
        
        # Check if we got an error result
        if "summary" in result and result["summary"].startswith("Error:"):
            raise Exception(result["summary"])
            
        # Update the job with results
        job.results.update(result)
        job.add_update("Podcast generated successfully", "complete")
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

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('data/podcasts', exist_ok=True)
    os.makedirs('data/research', exist_ok=True)
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)