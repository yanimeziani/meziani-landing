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

def validate_environment():
    """
    Validate that all required environment variables are set
    
    Returns:
        dict: Status of environment validation
    """
    import os
    required_vars = {
        'ANTHROPIC_API_KEY': 'Missing API key for Claude AI',
        'MODEL': 'Using default model claude-3-5-sonnet-20240620',
        'CREWAI_MEMORY_DB_PATH': 'Using default memory path /app/data/memory.db'
    }
    
    optional_vars = {
        'SERPER_API_KEY': 'Web search will use simulated results',
        'ELEVENLABS_API_KEY': 'Text-to-speech will use simulated audio'
    }
    
    status = {
        'valid': True,
        'missing_required': [],
        'missing_optional': [],
        'details': {}
    }
    
    # Check required variables
    for var, message in required_vars.items():
        if not os.environ.get(var):
            if var == 'ANTHROPIC_API_KEY':
                status['valid'] = False
                status['missing_required'].append(var)
                status['details'][var] = message
            else:
                # Set default values for non-critical vars
                if var == 'MODEL':
                    os.environ[var] = 'claude-3-5-sonnet-20240620'
                elif var == 'CREWAI_MEMORY_DB_PATH':
                    os.environ[var] = '/app/data/memory.db'
                status['details'][var] = message
    
    # Check optional variables
    for var, message in optional_vars.items():
        if not os.environ.get(var):
            status['missing_optional'].append(var)
            status['details'][var] = message
    
    return status

def run():
    """
    Run the podcast crew with default settings
    """
    # Validate environment first
    env_status = validate_environment()
    if not env_status['valid']:
        error_msg = f"Environment validation failed: {', '.join(env_status['missing_required'])}"
        raise ValueError(error_msg)
    
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        'hosts': ['Alex', 'Jamie']
    }
    
    try:
        from podcast.crew import PodcastCrew
        podcast_crew = PodcastCrew(topic=inputs['topic'], hosts=inputs['hosts'])
        result = podcast_crew.run()
        return result
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"An error occurred while running the crew: {e}\n{error_details}"
        raise Exception(error_msg)

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