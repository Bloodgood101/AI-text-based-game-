import json
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import gc

conversation_history = []

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"using device {device}")

model_name = "microsoft/DialoGPT-large"
tokenizer = AutoTokenizer.from_pretrained(model_name)
#Fine tooled for my machine
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.float16, #For my M1 pro chip
    low_cpu_mem_usage=True
)

# Set padding token to eos token if it doesn't exist
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = model.to(device)
model.eval()

def remove_repeated_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    unique_sentences = []
    for sentence in sentences:
        if sentence not in unique_sentences:
            unique_sentences.append(sentence)
        else:
            break
    return ' '.join(unique_sentences)

def clean_response(response_text, prompt):
    # Remove the prompt from the response
    stripped_response = response_text.replace(prompt, '').strip()

    # Split the stripped response text into lines
    lines = stripped_response.split('\n')

    combined_lines = " ".join(line.strip() for line in lines if line.strip())
    return remove_repeated_sentences(combined_lines)

def generate_response(prompt, max_length=150): #Max_length varies for device used
    try:
        inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
        input_ids = inputs["input_ids"].to(device)
        attention_mask = inputs["attention_mask"].to(device) #Moves all ids and masks for my device

        # Generate response
        with torch.no_grad():
            output = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                temperature=0.8,
                #repetition_penalty=1.1,
            )

        response = tokenizer.decode(output[0], skip_special_tokens=True)
        cleaned_response = clean_response(response, prompt)

        # Clean up memory
        del inputs, input_ids, attention_mask, output
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
        gc.collect()

        return cleaned_response

    except RuntimeError as e:
        if "out of memory" in str(e):
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            gc.collect()
            return "I'm sorry, I encountered a memory issue. Please try a shorter input."
        else:
            return f"I encountered an error: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def save_conversation(filename=None):
    if filename is None:
        filename = f"conversation_history.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(conversation_history, f, indent=2, ensure_ascii=False)
        print(f"conversation saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False

def load_conversation(filename):
    global conversation_history
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            conversation_history = json.load(f)
        print(f"loaded previous chat file")
        return True
    except FileNotFoundError:
        print(f"No conversation file found")
        return False
    except Exception as e:
        print(f"Error occurred at {e}")
        return False

def display_conversation_history():
    print("\n--- Conversation History ---")
    for i, entry in enumerate(conversation_history, 1):
        print(f"{i}. You: {entry['user_input']}")
        print(f"   Bot: {entry['model_response']}")
        print()


def main():
    global conversation_history

    print("Quentin: State your name, traveller.")
    name = input()
    print("Commands: 'exit' to quit, 'save' to save conversation, 'history' to show history")

    # Optional: Load previous conversation
    # load_conversation_from_file("conversation_history.json")

    while True:
        user_input = input(f"{name}: ").strip()

        if user_input.lower() == "exit":
            # Ask if user wants to save before exiting
            save_before_exit = input("Save conversation before exiting? (y/n): ").lower()
            if save_before_exit == 'y':
                save_conversation()
            print(generate_response(user_input))
            break

        elif user_input.lower() == "save":
            filename = input("Enter filename (or press enter for auto-generated): ").strip()
            if filename:
                save_conversation(filename)
            else:
                save_conversation()
            continue

        elif user_input.lower() == "history":
            display_conversation_history()
            continue

        elif user_input.lower() == "clear":
            conversation_history.clear()
            print("Conversation history cleared!")
            continue

        # Generate response
        response = generate_response(user_input)
        print("Quentin:", response)

        # Store both user input and model response with timestamp
        conversation_entry = {
            'user_input': user_input,
            'model_response': response
        }
        conversation_history.append(conversation_entry)

        # Optional: Auto-save every few interactions
        if len(conversation_history) % 10 == 0:  # Save every 5 exchanges
            print("Auto-saving conversation...")
            save_conversation("conversation_autosave.json")


if __name__ == "__main__":
    main()
