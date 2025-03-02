from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
import json
from datetime import datetime
import os
import dotenv

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

@CrewBase
class PodcastCrew():
    """Podcast creation crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self, topic, hosts=None, job_id=None, callback=None):
        """
        Initialize the podcast crew with specific parameters
        
        Args:
            topic (str): The podcast topic
            hosts (list, optional): List of podcast hosts
            job_id (str, optional): Unique job identifier
            callback (callable, optional): Callback function for job updates
        """
        self.topic = topic
        self.hosts = hosts or ["Alex", "Jamie"]
        self.job_id = job_id
        self.callback = callback

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            llm_config={
                "provider": "anthropic",
                "config": {
                    "model": os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'),
                    "temperature": 0.7,
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY', 'dummy-key'),
                }
            }
        )

    @agent
    def topic_curator(self) -> Agent:
        return Agent(
            config=self.agents_config['topic_curator'],
            verbose=True,
            llm_config={
                "provider": "anthropic",
                "config": {
                    "model": os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'),
                    "temperature": 0.7,
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY', 'dummy-key'),
                }
            }
        )

    @agent
    def script_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['script_writer'],
            verbose=True,
            llm_config={
                "provider": "anthropic",
                "config": {
                    "model": os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'),
                    "temperature": 0.7,
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY', 'dummy-key'),
                }
            }
        )

    @agent
    def audio_director(self) -> Agent:
        return Agent(
            config=self.agents_config['audio_director'],
            verbose=True,
            llm_config={
                "provider": "anthropic",
                "config": {
                    "model": os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'),
                    "temperature": 0.7,
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY', 'dummy-key'),
                }
            }
        )

    @task
    def research_task(self) -> Task:
        from podcast.tools.web_search import WebSearchTool
        
        return Task(
            config=self.tasks_config['research_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback,
            tools=[WebSearchTool()]
        )

    @task
    def topic_curation_task(self) -> Task:
        return Task(
            config=self.tasks_config['topic_curation_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback,
            expected_output=dict
        )

    @task
    def script_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['script_writing_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback,
            expected_output=str
        )

    @task
    def audio_production_task(self) -> Task:
        from podcast.tools.elevenlabs import ElevenLabsTool
        
        return Task(
            config=self.tasks_config['audio_production_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback,
            tools=[ElevenLabsTool()],
            expected_output=dict
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Podcast creation crew"""
        return Crew(
            agents=[
                self.researcher(),
                self.topic_curator(),
                self.script_writer(),
                self.audio_director()
            ],
            tasks=[
                self.research_task(),
                self.topic_curation_task(),
                self.script_writing_task(),
                self.audio_production_task()
            ],
            process=Process.sequential,
            verbose=True,
        )

    def run(self):
        """
        Run the podcast creation process
        
        Returns:
            dict: Results of the podcast creation process
        """
        # Check if API keys are set and validate configuration
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        serper_key = os.environ.get('SERPER_API_KEY')
        elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
        memory_db_path = os.environ.get('CREWAI_MEMORY_DB_PATH')
        model = os.environ.get('MODEL', 'claude-3-5-sonnet-20240620')
        
        # Validate memory DB path
        if memory_db_path:
            memory_dir = os.path.dirname(memory_db_path)
            if not os.path.exists(memory_dir):
                try:
                    os.makedirs(memory_dir, exist_ok=True)
                    if self.callback:
                        self.callback(f"Created memory directory: {memory_dir}", "debug")
                except Exception as e:
                    if self.callback:
                        self.callback(f"Failed to create memory directory: {str(e)}", "error")
        
        # Log configuration status (without showing the actual keys)
        if self.callback:
            self.callback(f"API keys available: Anthropic: {'Yes' if anthropic_key else 'No'}, "
                         f"Serper: {'Yes' if serper_key else 'No'}, "
                         f"ElevenLabs: {'Yes' if elevenlabs_key else 'No'}", "debug")
            self.callback(f"Using model: {model}", "debug")
            self.callback(f"Memory DB path: {memory_db_path}", "debug")
        
        # Check required API key
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required but not set")
        
        # Prepare tools for agents
        from podcast.tools.web_search import WebSearchTool
        from podcast.tools.elevenlabs import ElevenLabsTool
        
        # Create tools
        web_search_tool = WebSearchTool()
        elevenlabs_tool = ElevenLabsTool()
        
        # Set up inputs
        inputs = {
            'topic': self.topic,
            'hosts': self.hosts,
            'current_year': str(os.getenv('CURRENT_YEAR', '2025'))
        }
        
        # Set callback for CrewAI progress
        def task_callback(task_output):
            """Callback for CrewAI tasks"""
            if self.callback:
                # Type check task_output before trying to use .get()
                if isinstance(task_output, dict):
                    task_name = task_output.get('task_name', 'unknown')
                    self.callback(f"Task completed: {task_name}", 
                                 task_name.split('_')[0] if '_' in task_name else task_name)
                elif isinstance(task_output, str):
                    # Handle string task outputs
                    self.callback(f"Task completed with string output: {task_output[:50]}...", "processing")
                else:
                    # Handle other types
                    self.callback(f"Task completed with output type: {type(task_output).__name__}", "processing")
            return task_output
        
        try:
            # Create the crew with task callbacks
            crew_instance = self.crew()
            
            # Set task callbacks
            for task in crew_instance.tasks:
                task.human_input_callback = task_callback
            
            # Kickoff the crew
            if self.callback:
                self.callback("Starting CrewAI podcast generation process", "processing")
            
            # Run the crew
            results = crew_instance.kickoff(inputs=inputs)
            
            # Add debug information about the result type
            if self.callback:
                result_type = type(results).__name__
                self.callback(f"CrewAI result type: {result_type}", "debug")
                
                # Extra checking for unexpected result types
                if not isinstance(results, (dict, str)):
                    self.callback(f"Unexpected result type: {result_type}, converting to string", "debug")
                    results = str(results)
            
            # Debug output
            if self.callback:
                self.callback(f"CrewAI result type: {type(results)}", "debug")
                if isinstance(results, dict):
                    self.callback(f"CrewAI result keys: {list(results.keys())}", "debug")
                elif isinstance(results, str):
                    self.callback(f"CrewAI string result (first 100 chars): {results[:100]}...", "debug")
            
            # Process results based on type
            if isinstance(results, dict):
                # Dictionary result - process tasks from dictionary
                return {
                    "research": results.get('research_task', {}),
                    "summary": results.get('topic_curation_task', ''),
                    "script": results.get('script_writing_task', ''),
                    "audio_details": results.get('audio_production_task', {})
                }
            elif isinstance(results, str):
                # String result - convert to dictionary format
                output = {
                    "research": {},
                    "summary": "Generated by CrewAI",
                    "script": results,
                    "audio_details": {
                        "voice_instructions": f"Use a conversational tone for {', '.join(self.hosts)}."
                    }
                }
                if self.callback:
                    self.callback("Converted string result to structured format", "processing")
                return output
            else:
                raise ValueError(f"Unexpected result type from CrewAI: {type(results)}")
        
        except Exception as e:
            # Log the error
            error_msg = f"Error in crew.run(): {str(e)}"
            if self.callback:
                self.callback(error_msg, "error")
            
            # Return error result
            return {
                "research": {},
                "summary": f"Error: {str(e)}",
                "script": "",
                "audio_details": {}
            }
    
    def _convert_string_result(self, result_str):
        """Convert a string result to the expected dictionary format"""
        if self.callback:
            self.callback("Converting string result to dictionary", "processing")
        
        # Try to extract script and summary from the string
        lines = result_str.strip().split('\n')
        
        # Simple heuristic: first few lines are likely summary, rest is script
        summary = "\n".join(lines[:min(5, len(lines)//4)])
        script = result_str
        
        return {
            "research": {
                "sources": [
                    {"title": f"Research on {self.topic}", "url": "https://example.com/research"}
                ],
                "topics": [self.topic]
            },
            "summary": summary,
            "script": script,
            "audio_details": {
                "voice_instructions": f"Use a conversational tone for {', '.join(self.hosts)}."
            }
        }
    
    def _process_tasks_manually(self, inputs):
        """Process tasks manually when CrewAI fails"""
        if self.callback:
            self.callback("Processing tasks manually", "research")
        
        topic = inputs['topic']
        hosts = inputs['hosts']
        
        # 1. Research task - create simulated data
        research_data = {
            "results": [
                {
                    "title": f"Understanding {topic}",
                    "url": f"https://example.com/understanding-{topic.lower().replace(' ', '-')}",
                    "snippet": f"A comprehensive guide to {topic} with insights from industry experts and analysis of current trends.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "title": f"The Future of {topic}",
                    "url": f"https://example.com/future-of-{topic.lower().replace(' ', '-')}",
                    "snippet": f"Experts predict significant developments in {topic} over the next decade, with major implications for technology and society.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "title": f"{topic}: A Deep Dive",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-analysis",
                    "snippet": f"An in-depth analysis of {topic}, including historical context, current state, and future projections.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
        }
        
        if self.callback:
            self.callback(f"Research complete, found {len(research_data.get('results', []))} results", "research")
        
        # 2. Topic curation
        summary = f"This podcast explores {topic} from multiple angles, discussing its current state, challenges, and future implications."
        
        if self.callback:
            self.callback("Topic curation complete", "summarize")
        
        # 3. Script writing
        script = f"""
# {topic} Podcast Script

## Introduction
{hosts[0]}: Welcome to our podcast on {topic}! I'm {hosts[0]}.
{hosts[1]}: And I'm {hosts[1]}. Today we're diving deep into {topic}.

## Main Discussion
{hosts[0]}: Let's start by discussing why {topic} is so important today.
{hosts[1]}: Absolutely! The impact of {topic} can't be overstated.

## Recent Developments
{hosts[0]}: According to recent research, {topic} has seen significant advancements.
{hosts[1]}: That's right. Experts are predicting major changes in how we approach {topic}.

## Future Outlook
{hosts[0]}: What do you think the future holds for {topic}?
{hosts[1]}: I believe we'll see more integration with other technologies and wider adoption.

## Conclusion
{hosts[0]}: That wraps up our discussion on {topic}.
{hosts[1]}: Thanks for listening, and we'll see you next time!
"""
        
        if self.callback:
            self.callback("Script writing complete", "script")
        
        # 4. Audio production
        audio_details = {
            "voice_instructions": f"Use a conversational tone. {hosts[0]} should have a slightly deeper voice than {hosts[1]}.",
            "pacing": "Moderate pace with natural pauses between segments",
            "tone": "Informative but conversational"
        }
        
        if self.callback:
            self.callback("Audio production details complete", "voice")
        
        # Return the complete result
        return {
            "research": {
                "sources": [result for result in research_data.get('results', [])],
                "topics": [f"{topic} Overview", f"{topic} Challenges", f"Future of {topic}"]
            },
            "summary": summary,
            "script": script,
            "audio_details": audio_details
        }