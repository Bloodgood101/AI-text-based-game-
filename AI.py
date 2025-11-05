import tempfile
import threading

from llama_cpp import Llama
import json
import datetime
import os

from gtts import gTTS
import pygame
import tempfile

class Narrator:
    def __init__(self):
        pygame.mixer.init()
        self.current_audio_file = None

        #Above is for text to speech
        self.intro = None
        self.attributes = None
        self.name = None
        self.inventory = []
        self.llm = Llama(
            model_path="./models/llama-2-7b-chat.Q4_0.gguf",
            n_ctx=4096,
            n_batch=512,
            n_gpu_layers=1,
            verbose=False,
            use_mlock=True, #uses Metal for Apple
        )
        self.story_history = []
        self.log_file="gameLog.txt"
        self._init_logging()

    def speak(self, text):
        def _speakthread():
            try:
                clean_text = self._clean_text_for_tts(text)
                tts = gTTS(text=clean_text, lang="zh", slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    self.current_audio_file = temp_audio.name
                    tts.save(temp_audio.name)

                pygame.mixer.music.load(self.current_audio_file)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

                if self.current_audio_file and os.path.exists(self.current_audio_file):
                    os.unlink(self.current_audio_file)
                    self.current_audio_file = None

            except Exception as e:
                print(f"TTS error: {e}")

        tts_thread = threading.Thread(target=_speakthread())
        tts_thread.daemon = True
        tts_thread.start()

    def _clean_text_for_tts(self, text):
        import re
        clean_text = re.sub(r'[*_`#]', '', text)
        clean_text = re.sub(r'\[.*?\[\(.*?\)', '', text)
        clean_text = re.sub(r'\n+', '. ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        return clean_text.strip()

    def stop_speaking(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            os.unlink(self.current_audio_file)
            self.current_audio_file=None
    
    def _init_logging(self):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"New Game Session - {datetime.datetime.now()}\n")
            f.write(f"{'='*50}\n")
    
    def log_interaction(self, user_input, narrator_response):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] User: {user_input}\n")
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Narrator: {narrator_response}\n")
            f.write("-" * 80 + "\n")

    def create_system_prompt(self):
        return """
        You are the narrator for a text-based adventure game. From the user data and intro you have stored you must
        design an adventure for the user, based on all gathered facts, stats and the first five user responses. You can 
        use the {recent_context} to understand where the direction of where the story is going. Although the idea of 
        this program is that the user has full creative control, you must push them to stay on the story's trail so the
        story can be completed. Use the character's attributes to influence story outcomes and outcomes of actions. 
        Be creative with descriptions of everything, you are a narrator and you are painting the story, and progress the
        story through primarily player choices and actions. 
        """

    def generate_response(self, prompt):
        # Build context from recent history
        recent_context = "\n".join(
            self.story_history[-5:]) if self.story_history else self.intro

        system_prompt = self.create_system_prompt().format(
            recent_context=recent_context
        )

        full_prompt = f"{system_prompt}\n\nPlayer:{prompt}\nNarrator:"

        # Generate response
        response = self.llm(
            full_prompt,
            max_tokens=256,
            temperature=0.8,
            top_p=0.9,
            echo=False,
            stop=[f"Player:", "###", "Narrator:", "\n\nPlayer", "You:", "User:"] #simple stop mechanic
        )

        narration = response['choices'][0]['text'].strip()

        self.log_interaction(prompt, narration)

        self.story_history.append(f"User: {prompt}")
        self.story_history.append(f"Narrator: {narration}")

        """
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        """
        return narration

    def add_character_data(self, character_data):
        self.name=character_data['name']
        self.attributes=character_data['attributes']
        self.intro=character_data['story_prompt']

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nCHARACTER CREATED:\n")
            f.write(f"Name: {self.name}\n")
            f.write(f"Attributes: {self.attributes}\n")
            f.write(f"Story Prompt: {self.intro}\n")
            f.write(f"{'='*50}\n")

"""Import tensorflow for machine learning, need to learn basic storytelling and prompt understanding.
Use attributes to dictate character actions, attributes can be decreased and increased based on specific actions.
Story must finish within 200-500 prompts. Items? Other characters? No response should be longer than 200 words. 
Machine intelligence?"""

"""
if __name__ == "__main__":
"""


