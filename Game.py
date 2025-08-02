import AI

"""This is where the game is played, and saved. Implements the AI class, but only uses the main class to 
transition to the game."""

import tkinter as tk
from tkinter import scrolledtext

import tkinter as tk
from tkinter import scrolledtext


class ChatApplication:
    def __init__(self, root, character_data):
        self.root = root
        self.character_data = character_data
        self.root.title("Narrator Chat")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        # Create and configure fonts
        self.response_font = ("Arial", 11)
        self.input_font = ("Arial", 10)

        # Create narrator response section
        self.create_response_section()

        # Create user input section
        self.create_input_section()

        # Sample initial message
        welcome_msg = (
            f"Welcome {character_data['name']}! I'm your narrator.\n"
            f"We're beginning your story about: {character_data['story_prompt'][:500]}..."
        )
        self.display_narrator_response(welcome_msg)

    def create_response_section(self):
        # Response frame
        response_frame = tk.LabelFrame(self.root, text="Narrator Responses", padx=10, pady=10)
        response_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        # Scrolled Text widget for responses
        self.response_area = scrolledtext.ScrolledText(
            response_frame,
            wrap=tk.WORD,
            font=self.response_font,
            state='disabled',
            padx=10,
            pady=10,
            bg='#f0f0f0'
        )
        self.response_area.grid(row=0, column=0, sticky="nsew")

        # Configure tags for different message types
        self.response_area.tag_configure('narrator', foreground='blue', lmargin1=10, lmargin2=10, rmargin=10)
        self.response_area.tag_configure('user', foreground='green', lmargin1=10, lmargin2=10, rmargin=10)

    def create_input_section(self):
        # Input frame
        input_frame = tk.Frame(self.root)
        input_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Prompt label
        tk.Label(input_frame, text="Your Prompt:", font=self.input_font).grid(row=0, column=0, sticky="w")

        # Text widget for user input (multi-line)
        self.user_input = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            font=self.input_font,
            padx=10,
            pady=10
        )
        self.user_input.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.user_input.focus_set()

        # Submit button
        submit_btn = tk.Button(
            input_frame,
            text="Send to Narrator",
            command=self.process_input,
            bg='#4CAF50',
            fg='white',
            font=self.input_font
        )
        submit_btn.grid(row=2, column=0, sticky="e", pady=(10, 0))

        # Configure grid weights
        input_frame.columnconfigure(0, weight=1)

    def display_narrator_response(self, message):
        self.response_area.config(state='normal')
        self.response_area.insert(tk.END, "Narrator: " + message + "\n\n", 'narrator')
        self.response_area.config(state='disabled')
        # Auto-scroll to bottom
        self.response_area.see(tk.END)

    def process_input(self):
        # Get user input and clear the input box
        user_text = self.user_input.get("1.0", tk.END).strip()
        if not user_text:
            return

        self.user_input.delete("1.0", tk.END)

        # Display user message in response area
        self.response_area.config(state='normal')
        self.response_area.insert(tk.END, "You: " + user_text + "\n", 'user')
        self.response_area.config(state='disabled')
        self.response_area.see(tk.END)

        # Process the input and generate narrator response
        self.generate_response(user_text)

    def generate_response(self, user_input):
        # This is where you would connect to your AI/Narrator service
        # For demonstration, we'll create simple responses

        # Simulate processing delay
        self.root.after(1000, lambda: self.display_narrator_response(AI.generate_response(user_input)))

"""
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()
"""
