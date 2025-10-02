import openai
from openai import OpenAI

knowledge_base = []
prompts = []
inventory = []

class Character:
    def __init__(self, name, attributes, intro):
        self.name = name,
        self.attributes = attributes,
        self.intro = intro

    def __repr__(self):
        return f"Character(name={self.name}, attributes={self.attributes}"

def add_character_data(character_data):
    """Add character data to the knowledge base"""
    character = Character(
        name=character_data['name'],
        attributes=character_data['attributes'],
        intro=character_data['story_prompt']
    )
    print(f"Added to knowledge base: {character}")

def generate_response(user_input):
    openai.api_key = "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"
    response = openai.ChatCompletion.create(
        model="gpt-0.28",
        input=user_input
    )
    return response.output_text

"""Import tensorflow for machine learning, need to learn basic storytelling and prompt understanding.
Use attributes to dictate character actions, attributes can be decreased and increased based on specific actions.
Story must finish within 200-500 prompts. Items? Other characters? No response should be longer than 200 words. 
Machine intelligence?"""



