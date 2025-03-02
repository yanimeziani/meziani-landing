#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from media.crew import Media

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    from crewai import Agent, Crew, Process, Task
    import os
    
    # Set the default model to Anthropic
    os.environ["OPENAI_API_KEY"] = ""  # Clear OpenAI key to prevent fallback
    
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        # Create the Media crew with explicit Anthropic config
        media_crew = Media().crew()
        
        # Set Anthropic as the LLM for all agents
        for agent in media_crew.agents:
            agent.llm = {
                'provider': 'anthropic',
                'model': os.environ.get('MODEL', 'claude-3-5-sonnet-20240620')
            }
        
        result = media_crew.kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Media().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Media().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Media().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
