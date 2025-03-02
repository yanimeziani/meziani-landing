#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run_podcast_generation(topic=None, hosts=None):
    """
    Run podcast generation with optional topic and hosts
    
    Args:
        topic (str, optional): Podcast topic. Defaults to None.
        hosts (list, optional): List of podcast hosts. Defaults to None.
    
    Returns:
        dict: Podcast generation results
    """
    from podcast.crew import PodcastCrew
    
    # Set default topic if not provided
    topic = topic or 'AI and Technology Trends'
    hosts = hosts or ['Alex', 'Jamie']
    
    # Create and run the podcast crew
    crew = PodcastCrew(
        topic=topic, 
        hosts=hosts
    )
    
    result = crew.run()
    return result

def run():
    """
    Run the podcast crew with default settings
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        'hosts': ['Alex', 'Jamie']
    }
    
    try:
        from podcast.crew import PodcastCrew
        result = PodcastCrew().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations
    """
    inputs = {
        "topic": "AI LLMs",
        "hosts": ['Alex', 'Jamie']
    }
    try:
        from podcast.crew import PodcastCrew
        PodcastCrew().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task
    """
    try:
        from podcast.crew import PodcastCrew
        PodcastCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results
    """
    inputs = {
        "topic": "AI LLMs",
        "hosts": ['Alex', 'Jamie']
    }
    try:
        from podcast.crew import PodcastCrew
        PodcastCrew().crew().test(
            n_iterations=int(sys.argv[1]), 
            openai_model_name=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    # Add any necessary initialization or command-line interface logic
    pass