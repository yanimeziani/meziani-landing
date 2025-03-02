from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os

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
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY'),
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
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY'),
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
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY'),
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
                    "anthropic_api_key": os.environ.get('ANTHROPIC_API_KEY'),
                }
            }
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback
        )

    @task
    def topic_curation_task(self) -> Task:
        return Task(
            config=self.tasks_config['topic_curation_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback
        )

    @task
    def script_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['script_writing_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback
        )

    @task
    def audio_production_task(self) -> Task:
        return Task(
            config=self.tasks_config['audio_production_task'],
            context=[self.topic, str(self.hosts)],
            human_input_callback=self.callback
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
        inputs = {
            'topic': self.topic,
            'hosts': self.hosts,
            'current_year': str(os.getenv('CURRENT_YEAR', '2025'))
        }
        
        # Kickoff the crew and process results
        result = self.crew().kickoff(inputs=inputs)
        
        # Check if result is a string or dictionary
        if isinstance(result, str):
            # Handle string result
            if self.callback:
                self.callback("Received result as string, processing accordingly", "processing")
            return {
                "research": {},
                "summary": result,
                "script": result,
                "audio_details": {}
            }
        else:
            # Handle dictionary result
            return {
                "research": result.get('research', {}),
                "summary": result.get('topic_curation', ''),
                "script": result.get('script_writing', ''),
                "audio_details": result.get('audio_production', {})
            }