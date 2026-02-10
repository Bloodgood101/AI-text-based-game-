import tempfile
import threading
import os
import re
import json
import datetime

from llama_cpp import Llama
from gtts import gTTS

# Conditionally import pygame only if available
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not installed. TTS will be disabled.")


class Narrator:
    def __init__(self):
        self.current_audio_file = None
        self.pygame_initialized = False

        # Initialize pygame mixer with macOS compatibility
        if PYGAME_AVAILABLE:
            try:
                # Try different initialization parameters for macOS
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
                pygame.mixer.init()
                self.pygame_initialized = True
                print("Pygame mixer initialized successfully")
            except pygame.error as e:
                print(f"Warning: Could not initialize pygame mixer: {e}")
                print("TTS functionality will be disabled.")
                self.pygame_initialized = False
        else:
            self.pygame_initialized = False

        # Above is for text to speech
        self.intro = None
        self.attributes = None
        self.name = None
        self.inventory = [] #to implement later
        self.setting = None

        self.first_response = True #this is for system_prompt issues

        # Initialize LLM
        self.llm = Llama(
            model_path="./models/mythomax-l2-13b.Q4_K_M.gguf",
            n_ctx=4096, #longer context use 8192
            n_batch=192, #for bigger LLMs use lower n_batch
            n_gpu_layers=28, #using -1 causes an out of memory error for some models, so 28 is apparently the next-most optimum for this model
            verbose=False,
            use_mlock=True,  # uses Metal for Apple
            n_threads=6, #Mac usually has between 8-10 cores so 6 is an ok value
            seed=1337, #seeds are for consistency
        )

        self.story_history = []
        self.log_file = "gameLog.txt"
        self._init_logging()

    def speak(self, text):
        # Check if TTS is available
        if not self.pygame_initialized:
            print("TTS disabled: pygame mixer not initialized")
            return

        def _speak_thread():
            try:
                clean_text = self._clean_text_for_tts(text)
                tts = gTTS(text=clean_text, lang="zh", slow=False)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    self.current_audio_file = temp_audio.name
                    tts.save(temp_audio.name)

                pygame.mixer.music.load(self.current_audio_file)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)  # More reliable than wait()

                # Clean up the temporary file
                if self.current_audio_file and os.path.exists(self.current_audio_file):
                    os.unlink(self.current_audio_file)
                    self.current_audio_file = None

            except Exception as e:
                print(f"TTS error: {e}")
                # Clean up any leftover temp file
                if self.current_audio_file and os.path.exists(self.current_audio_file):
                    try:
                        os.unlink(self.current_audio_file)
                    except:
                        pass
                    self.current_audio_file = None

        # Start TTS in a separate thread (FIXED: removed parentheses after _speak_thread)
        tts_thread = threading.Thread(target=_speak_thread)
        tts_thread.daemon = True
        tts_thread.start()

    def _clean_text_for_tts(self, text):
        # Remove markdown-like formatting
        clean_text = re.sub(r'[*_`#]', '', text)
        # Remove any special patterns
        clean_text = re.sub(r'\[.*?\]', '', clean_text)
        # Replace multiple newlines with periods
        clean_text = re.sub(r'\n+', '. ', clean_text)
        # Collapse multiple spaces
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    def stop_speaking(self):
        if PYGAME_AVAILABLE and self.pygame_initialized:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            if self.current_audio_file and os.path.exists(self.current_audio_file):
                try:
                    os.unlink(self.current_audio_file)
                except:
                    pass
                self.current_audio_file = None

    def _init_logging(self):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.truncate(0) #clears file before use
            f.seek(0) #must move cursor to start of the file as it can cause errors
            f.write(f"New Game Session - {datetime.datetime.now()}\n")
            f.write(f"{'=' * 50}\n")

    def log_interaction(self, user_input, narrator_response):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] User: {user_input}\n")
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Narrator: {narrator_response}\n")
            f.write("-" * 80 + "\n")

    def create_system_prompt(self):
        return """
        Use only the information you've been fed, and using only the information provided, give the user a story, 
        this is everything that is passed through the character_creation_log.json and gameLog.txt file. Think of 
        yourself as a narrator or storyteller, weaving a story through the user's decisions and actions, until you reach 
        a reasonable end. Be descriptive when describing new places and situations, you are also world-building for the
        user. Whenever a potential decision or action appears in your storytelling make sure to stop so the user can decide 
        what the next move should be. 
        When the user engages in attribute-based actions (strength, dexterity, luck, charisma, intelligence),
        incorporate the outcome into the ongoing narrative. Continue the story naturally based on whether
        the action succeeded or failed, and consider any attribute improvements that may have occurred.
        Use the character's attributes and the current story context to create compelling narrative responses.
        Always advance the story forward, building upon previous events and character development.
        """

    def generate_response(self, prompt):
        #Check if this is the first response
        if self.first_response:
            #For the first response add all necessary data, but only for the first time
            system_prompt = self.create_system_prompt()
            #Include character intro too just in case
            context = f"{system_prompt}\n\n{self.intro if self.intro else ''}"
            self.first_response = False
        else:
            #context will be story_history
            context = ""

        if self.story_history:
            #get last ten messages from conversation for context
            recent_messages = self.story_history[-10:]
            history_context = "\n".join(recent_messages)
            if context:
                context = f"{context}\n\nRecent Story:\n{history_context}"
            else:
                context = history_context

        # Build the full prompt
        if context:
            full_prompt = f"{context}\n\nPlayer: {prompt}\nNarrator:"
        else:
            full_prompt = f"Player: {prompt}\nNarrator:"

        # Generate response
        try:
            response = self.llm(
                full_prompt,
                max_tokens=1024, #this is character limit it allows to output, still figuring out if it is needed
                temperature=0.85, #I like between 0.8 and 0.9
                top_p=0.95,
                top_k = 40, #for better sampling
                repeat_penalty=1.1, #stop repeating the same things over and over
                echo=False,
                stop=["Player:", "###", "Narrator:", "\n\nPlayer", "You:", "User:"]
            )

            narration = response['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            narration = "The story continues..."

        # Log and update history
        self.log_interaction(prompt, narration)
        self.story_history.append(f"Player: {prompt}")
        self.story_history.append(f"Narrator: {narration}")

        return narration


    def add_character_data(self, character_data):
        self.name = character_data['name']
        self.attributes = character_data['attributes']
        self.intro = character_data['story_prompt']
        self.setting = character_data['setting']

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nCHARACTER CREATED:\n")
            f.write(f"Name: {self.name}\n")
            f.write(f"Attributes: {self.attributes}\n")
            f.write(f"Setting: {self.setting}\n")
            f.write(f"Story Prompt: {self.intro}\n")