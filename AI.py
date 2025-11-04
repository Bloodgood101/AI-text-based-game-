from llama_cpp import Llama
import json
import datetime
import os

class Narrator:
    def __init__(self):
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
        return """"""

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


