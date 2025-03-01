"""
Podcast creation crew module for generating podcast content using CrewAI.
"""
import os
import traceback
from datetime import datetime

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import dotenv

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

@CrewBase
class PodcastCrew:
    """Podcast creation crew"""

    # Keep these as string attributes for compatibility with CrewBase
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
        """Creates the researcher agent."""
        return Agent(
            role=f"Spécialiste de recherche sur {self.topic}",
            goal="Effectuer des recherches complètes sur le sujet du podcast",
            backstory="Vous êtes un chercheur québécois spécialisé en recherche d'information",
            verbose=True,
            llm_config={
                "provider": "ollama",
                "config": {
                    "model": os.environ.get('MODEL', 'deepseek-coder:7b'),
                    "temperature": 0.7,
                    "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                }
            }
        )

    @agent
    def topic_curator(self) -> Agent:
        """Creates the topic curator agent."""
        return Agent(
            role="Curateur de sujets de podcast",
            goal="Sélectionner et affiner les sujets les plus captivants",
            backstory="Vous avez un sens aigu pour identifier les sujets tendance québécois",
            verbose=True,
            llm_config={
                "provider": "ollama",
                "config": {
                    "model": os.environ.get('MODEL', 'deepseek-coder:7b'),
                    "temperature": 0.7,
                    "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                }
            }
        )

    @agent
    def script_writer(self) -> Agent:
        """Creates the script writer agent."""
        return Agent(
            role="Rédacteur de scripts de podcast",
            goal="Transformer les résultats de recherche en un script conversationnel",
            backstory="Vous maîtrisez le français québécois et ses expressions colorées",
            verbose=True,
            llm_config={
                "provider": "ollama",
                "config": {
                    "model": os.environ.get('MODEL', 'deepseek-coder:7b'),
                    "temperature": 0.7,
                    "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                }
            }
        )

    @agent
    def audio_director(self) -> Agent:
        """Creates the audio director agent."""
        return Agent(
            role="Spécialiste de production audio de podcast",
            goal="Fournir des conseils pour la production audio du podcast",
            backstory="Vous connaissez les nuances de l'accent québécois",
            verbose=True,
            llm_config={
                "provider": "ollama",
                "config": {
                    "model": os.environ.get('MODEL', 'deepseek-coder:7b'),
                    "temperature": 0.7,
                    "base_url": os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                }
            }
        )

    @task
    def research_task(self) -> Task:
        """Creates the research task."""
        try:
            from podcast.tools.web_search import WebSearchTool
            
            task_instance = Task(
                description=f"Research on {self.topic} for a French Quebec podcast",
                expected_output=f"Comprehensive research information about {self.topic} including key facts, trends, and expert opinions",
                agent=self.researcher()
            )
            
            # Add tools separately
            task_instance.tools = [WebSearchTool()]
            
            # Callback is handled at the Crew level, not task level in newer CrewAI versions
            
            return task_instance
        except ImportError:
            # Fallback to local import if package import fails
            from podcast.src.podcast.tools.web_search import WebSearchTool
            
            task_instance = Task(
                description=f"Research on {self.topic} for a French Quebec podcast",
                expected_output=f"Comprehensive research information about {self.topic} including key facts, trends, and expert opinions",
                agent=self.researcher()
            )
            
            # Add tools separately
            task_instance.tools = [WebSearchTool()]
            
            # Callback is handled at the Crew level, not task level in newer CrewAI versions
            
            return task_instance

    @task
    def topic_curation_task(self) -> Task:
        """Creates the topic curation task."""
        task_instance = Task(
            description=f"Curate topics about {self.topic} for a French Quebec podcast",
            expected_output=f"A curated list of engaging subtopics and angles for a podcast about {self.topic}, tailored for a Quebec audience",
            agent=self.topic_curator()
        )
        
        # Callback is handled at the Crew level, not task level in newer CrewAI versions
        
        return task_instance

    @task
    def script_writing_task(self) -> Task:
        """Creates the script writing task."""
        task_instance = Task(
            description=f"Write a podcast script in French Quebec style about {self.topic} for hosts {self.hosts[0]} and {self.hosts[1]}",
            expected_output="A complete podcast script with dialogue for both hosts, formatted with clear sections and including Quebec French expressions",
            agent=self.script_writer()
        )
        
        # Callback is handled at the Crew level, not task level in newer CrewAI versions
        
        return task_instance

    @task
    def audio_production_task(self) -> Task:
        """Creates the audio production task."""
        try:
            from podcast.tools.elevenlabs import ElevenLabsTool
            
            task_instance = Task(
                description=f"Create audio production guidelines for a French Quebec podcast about {self.topic} using ElevenLabs voices Alex and Simon",
                expected_output="Detailed audio production guidelines including voice profiles, tone instructions, and technical specifications for a Quebec-accent podcast",
                agent=self.audio_director()
            )
            
            # Add tools separately
            task_instance.tools = [ElevenLabsTool()]
            
            # Callback is handled at the Crew level, not task level in newer CrewAI versions
            
            return task_instance
        except ImportError:
            # Fallback to local import if package import fails
            from podcast.src.podcast.tools.elevenlabs import ElevenLabsTool
            
            task_instance = Task(
                description=f"Create audio production guidelines for a French Quebec podcast about {self.topic} using ElevenLabs voices Alex and Simon",
                expected_output="Detailed audio production guidelines including voice profiles, tone instructions, and technical specifications for a Quebec-accent podcast",
                agent=self.audio_director()
            )
            
            # Add tools separately
            task_instance.tools = [ElevenLabsTool()]
            
            # Callback is handled at the Crew level, not task level in newer CrewAI versions
            
            return task_instance

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
        # Check configuration
        ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        serper_key = os.environ.get('SERPER_API_KEY')
        elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
        memory_db_path = os.environ.get('CREWAI_MEMORY_DB_PATH')
        model = os.environ.get('MODEL', 'deepseek-coder:7b')
        
        # Validate memory DB path
        if memory_db_path:
            memory_dir = os.path.dirname(memory_db_path)
            if not os.path.exists(memory_dir):
                try:
                    os.makedirs(memory_dir, exist_ok=True)
                    if self.callback:
                        self.callback(f"Created memory directory: {memory_dir}", "debug")
                except (OSError, IOError) as e:
                    if self.callback:
                        self.callback(f"Failed to create memory directory: {str(e)}", "error")
        
        # Log configuration status
        if self.callback:
            self.callback(f"API configuration: Ollama URL: {ollama_base_url}, "
                         f"Serper: {'Yes' if serper_key else 'No'}, "
                         f"ElevenLabs: {'Yes' if elevenlabs_key else 'No'}", "debug")
            self.callback(f"Using model: {model}", "debug")
            self.callback(f"Memory DB path: {memory_db_path}", "debug")
        
        
        # Set up inputs
        inputs = {
            'topic': self.topic,
            'hosts': self.hosts,
            'current_year': str(os.getenv('CURRENT_YEAR', '2025'))
        }
        
        # Set callback for CrewAI progress
        def task_callback(task_output):
            """Callback for CrewAI tasks with improved error handling"""
            if not self.callback:
                return task_output
                
            # Debug the task_output type
            task_output_type = type(task_output).__name__
            self.callback(f"DEBUG: Task callback received type: {task_output_type}", "debug")
            
            try:
                # Handle dictionary output
                if isinstance(task_output, dict):
                    # Safely extract task name using dict methods, not attribute access
                    task_name = task_output.get('task_name', 'unknown_task')
                    
                    # Debug the dictionary keys
                    self.callback(f"DEBUG: Dict keys: {list(task_output.keys())}", "debug")
                    
                    # Extract the task type from the name
                    task_type = task_name.split('_')[0] if '_' in task_name else task_name
                    self.callback(f"Task completed: {task_name}", task_type)
                
                # Handle string output
                elif isinstance(task_output, str):
                    # Create a preview with length limit
                    max_preview_len = 50
                    preview = (task_output[:max_preview_len] + "...") if len(task_output) > max_preview_len else task_output
                    self.callback(f"Task produced string: {preview}", "processing")
                
                # Handle other types (like None, int, etc.)
                else:
                    self.callback(f"Task produced {task_output_type} output", "processing")
            
            except (ValueError, TypeError, KeyError) as e:
                # Catch any errors in the callback processing itself
                self.callback(f"Error in task callback: {str(e)}", "error")
                
            return task_output
        
        try:
            # Create the crew with task callbacks
            crew_instance = self.crew()
            
            # In newer CrewAI versions, callbacks are handled differently
            # No need to set task.human_input_callback directly
            
            # Kickoff the crew
            if self.callback:
                self.callback("Starting CrewAI podcast generation process", "processing")
            
            # Run the crew
            if self.callback:
                self.callback("Starting CrewAI execution with inputs: " + str(inputs), "debug")
                
            results = crew_instance.kickoff(inputs=inputs)
            
            # Debug the results in detail
            if self.callback:
                # Get the type
                result_type = type(results).__name__
                self.callback(f"DEBUG: CrewAI result type: {result_type}", "debug")
                
                # For string results, show a preview
                if isinstance(results, str):
                    max_preview = 100
                    preview = (results[:max_preview] + "...") if len(results) > max_preview else results
                    self.callback(f"DEBUG: String result preview: {preview}", "debug")
                
                # For dict results, show the keys and check value types
                elif isinstance(results, dict):
                    keys = list(results.keys())
                    self.callback(f"DEBUG: Dict result keys: {keys}", "debug")
                    
                    # Check value types for each key
                    for key in keys:
                        value_type = type(results[key]).__name__
                        self.callback(f"DEBUG: Key '{key}' has value type: {value_type}", "debug")
                        
                        # For dict values, show their keys too
                        if isinstance(results[key], dict):
                            inner_keys = list(results[key].keys())
                            self.callback(f"DEBUG: Inner keys for '{key}': {inner_keys}", "debug")
                
                # For None or other types
                else:
                    self.callback(f"DEBUG: Result value: {str(results)}", "debug")
                    
                # Extra checking for unexpected result types
                if not isinstance(results, (dict, str)) and results is not None:
                    self.callback(f"Converting {result_type} to string for processing", "debug")
                    results = str(results)
            
            # Process results based on type with safer access patterns
            if isinstance(results, dict):
                try:
                    # Dictionary result - safely extract using .get() method with defaults
                    output = {
                        "research": results.get('research_task', {}),
                        "summary": results.get('topic_curation_task', ''),
                        "script": results.get('script_writing_task', ''),
                        "audio_details": results.get('audio_production_task', {})
                    }
                    
                    # If any key is missing or None, check for alternate keys
                    if not output["research"]:
                        # Look for research data in a different format
                        for key in results.keys():
                            if 'research' in key.lower():
                                output["research"] = results[key]
                                break
                    
                    # Validate script content    
                    if not output["script"]:
                        # Try to find script in other keys
                        for key in results.keys():
                            if 'script' in key.lower() or 'writing' in key.lower():
                                output["script"] = results[key]
                                break
                                
                    # If still no script, try to use the fallback
                    if not output["script"] and results:
                        self.callback("No script found in results, generating fallback script", "warning")
                        # Use the script generation function from _process_tasks_manually
                        fallback_script = self._generate_fallback_script(self.topic, self.hosts)
                        output["script"] = fallback_script
                        
                    return output
                except (KeyError, AttributeError, TypeError) as e:
                    self.callback(f"Error processing dictionary result: {str(e)}", "error")
                    # Fall through to fallback handling
            
            elif isinstance(results, str):
                # String result - use our conversion method
                output = self._convert_string_result(results)
                if self.callback:
                    self.callback("Converted string result to structured format", "processing")
                return output
                
            elif results is None:
                # Handle None result
                if self.callback:
                    self.callback("CrewAI returned None result, using fallback", "warning")
                return self._process_tasks_manually(inputs)
                
            else:
                # For any other type, try to process manually
                if self.callback:
                    self.callback(f"Unexpected result type: {type(results).__name__}, using fallback", "warning")
                return self._process_tasks_manually(inputs)
        
        except (ValueError, RuntimeError, KeyError) as e:
            # Log the error with more details
            error_msg = f"Error in crew.run(): {str(e)}"
            if self.callback:
                self.callback(error_msg, "error")
                
                # Try to get more error details
                tb = traceback.format_exc()
                self.callback(f"Error details: {tb}", "debug")
            
            # Try to recover using manual processing
            try:
                self.callback("Attempting recovery with manual processing", "warning")
                return self._process_tasks_manually(inputs)
            except (ValueError, KeyError) as recovery_error:
                # Complete failure - return minimal error result
                self.callback(f"Recovery failed: {str(recovery_error)}", "error")
                return {
                    "research": {},
                    "summary": f"Error: {str(e)}",
                    "script": self._process_tasks_manually(inputs)["script"],
                    "audio_details": {
                        "voice_instructions": f"Use a conversational tone for {', '.join(self.hosts)}."
                    }
                }
    
    def _generate_fallback_script(self, topic, hosts):
        """Generate a basic script when other methods fail"""
        if self.callback:
            self.callback("Generating fallback script", "script")
            
        # Basic script template with the given topic and hosts
        script = f"""
# {topic} Podcast Script

## Introduction
{hosts[0]}: Bonjour et bienvenue à notre podcast sur {topic}! Je suis {hosts[0]}.
{hosts[1]}: Et moi c'est {hosts[1]}. Aujourd'hui on plonge dans le sujet de {topic}.

## Discussion Principale
{hosts[0]}: Commençons par discuter pourquoi {topic} est si important aujourd'hui.
{hosts[1]}: Absolument! L'impact de {topic} est vraiment considérable, tabarnouche!

## Développements Récents
{hosts[0]}: Selon des recherches récentes, {topic} a connu des avancées significatives.
{hosts[1]}: C'est vrai. Les experts prévoient des changements majeurs dans notre approche de {topic}.

## Perspectives d'Avenir
{hosts[0]}: Qu'est-ce que tu penses que l'avenir réserve pour {topic}?
{hosts[1]}: Je crois qu'on va voir plus d'intégration avec d'autres technologies et une adoption plus large.

## Conclusion
{hosts[0]}: Ça conclut notre discussion sur {topic}.
{hosts[1]}: Merci d'avoir écouté, et à la prochaine fois!
"""
        return script
        
    def _convert_string_result(self, result_str):
        """Convert a string result to the expected dictionary format"""
        if self.callback:
            self.callback("Converting string result to dictionary", "processing")
        
        try:
            # Try to extract script and summary from the string
            lines = result_str.strip().split('\n')
            
            # Simple heuristic: first few lines are likely summary, rest is script
            summary_line_count = min(5, len(lines)//4)
            summary = "\n".join(lines[:summary_line_count]) if summary_line_count > 0 else "Generated podcast script"
            script = result_str
            
            # Validate if it looks like a script
            if not any(host in script for host in self.hosts):
                self.callback("String result doesn't look like a script, generating fallback", "warning")
                script = self._generate_fallback_script(self.topic, self.hosts)
            
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
                    "voice_instructions": f"Use a conversational tone for {', '.join(self.hosts)}.",
                    "profils_voix": {
                        "Alex": {"voice_id": "alex", "caracteristiques": "Voix masculine avec accent québécois"},
                        "Simon": {"voice_id": "simon", "caracteristiques": "Voix masculine avec accent québécois"}
                    }
                }
            }
        except (ValueError, IndexError) as e:
            self.callback(f"Error in string conversion: {str(e)}, using fallback", "error")
            return self._process_tasks_manually({"topic": self.topic, "hosts": self.hosts})
    
    def _process_tasks_manually(self, inputs):
        """Process tasks manually when CrewAI fails"""
        if self.callback:
            self.callback("Processing tasks manually", "research")
        
        topic = inputs.get('topic', self.topic)
        hosts = inputs.get('hosts', self.hosts)
        
        # 1. Research task - create simulated data in French
        research_data = {
            "results": [
                {
                    "title": f"Comprendre {topic}",
                    "url": f"https://example.com/comprendre-{topic.lower().replace(' ', '-')}",
                    "snippet": f"Un guide complet sur {topic} avec des perspectives d'experts et une analyse des tendances actuelles.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "title": f"L'avenir de {topic}",
                    "url": f"https://example.com/avenir-de-{topic.lower().replace(' ', '-')}",
                    "snippet": f"Les experts prédisent des développements significatifs dans {topic} au cours de la prochaine décennie, avec des implications majeures pour la technologie et la société.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "title": f"{topic}: Une analyse approfondie",
                    "url": f"https://example.com/{topic.lower().replace(' ', '-')}-analyse",
                    "snippet": f"Une analyse en profondeur de {topic}, incluant le contexte historique, l'état actuel et les projections futures.",
                    "date": datetime.now().strftime("%Y-%m-%d")
                }
            ]
        }
        
        if self.callback:
            self.callback(f"Recherche terminée, {len(research_data.get('results', []))} résultats trouvés", "research")
        
        # 2. Topic curation - in French
        summary = f"Ce podcast explore {topic} sous plusieurs angles, discutant de son état actuel, ses défis et ses implications futures. Créé avec un accent québécois authentique."
        
        if self.callback:
            self.callback("Sélection de sujets terminée", "summarize")
        
        # 3. Script writing - in Quebec French
        script = self._generate_fallback_script(topic, hosts)
        
        if self.callback:
            self.callback("Rédaction du script terminée", "script")
        
        # 4. Audio production - with Quebec French specifications
        audio_details = {
            "profils_voix": {
                hosts[0]: {"voice_id": "alex", "caracteristiques": "Voix masculine avec accent québécois authentique"},
                hosts[1]: {"voice_id": "simon", "caracteristiques": "Voix masculine avec accent québécois authentique"}
            },
            "rythme": "Rythme modéré avec des pauses naturelles entre les segments",
            "ton": "Informatif mais conversationnel, avec expressions québécoises",
            "specs_audio": {
                "format": "mp3",
                "bitrate": "192kbps",
                "traitement": "Optimisé pour la clarté des voix"
            },
            "accentuation_quebecoise": "Utiliser des expressions typiquement québécoises comme 'tabarnouche', 'pantoute', 'c'est pas pire'"
        }
        
        if self.callback:
            self.callback("Détails de production audio terminés", "voice")
        
        # Return the complete result
        return {
            "research": {
                "sources": [result for result in research_data.get('results', [])],
                "topics": [f"Aperçu de {topic}", f"Défis de {topic}", f"Avenir de {topic}"]
            },
            "summary": summary,
            "script": script,
            "audio_details": audio_details
        }