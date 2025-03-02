from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from langchain_anthropic import ChatAnthropic  # Import Anthropic's LangChain integration

@CrewBase
class Media():
    """Media crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def get_llm(self):
        """Set up the Anthropic LLM"""
        # Use LangChain's ChatAnthropic integration
        return ChatAnthropic(
            model_name=os.environ.get('MODEL', 'claude-3-5-sonnet-20240620'),
            anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
            temperature=0.7
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            llm=self.get_llm()  # Use the LLM we set up
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True,
            llm=self.get_llm()  # Use the LLM we set up
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Media crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )