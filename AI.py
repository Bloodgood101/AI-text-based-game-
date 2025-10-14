from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

knowledge_base = []
prompts = []
inventory = []

MODELS = {
    "small": "gpt2",
    "medium": "gpt2-medium",
    "large": "gpt2-large",
    "xl": "gpt2-xl"
}

def load_model(size="small"):
    print("Getting LLM...")
    if size not in MODELS:
        raise ValueError("Size not found")
    
    model_name = MODELS[size]
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("LLM grabbed...")
    return tokenizer, model 


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

"""Import tensorflow for machine learning, need to learn basic storytelling and prompt understanding.
Use attributes to dictate character actions, attributes can be decreased and increased based on specific actions.
Story must finish within 200-500 prompts. Items? Other characters? No response should be longer than 200 words. 
Machine intelligence?"""

if __name__ == "__main__":
    load_model()



