from AI import Narrator
import tkinter as tk
from tkinter import scrolledtext
import threading
import time


class ChatApplication:
    def __init__(self, root, character_data):
        self.root = root
        self.character_data = character_data
        self.root.title("Narrator Chat")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        self.tts_enabled = tk.BooleanVar(value=True)  # for text to speech
        self.is_typing = False  # Track if narrator is currently "typing"
        self.current_typing_thread = None  # Track current typing thread
        self.typing_position = None  # Track where typing starts

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
        self.display_narrator_response(welcome_msg, skip_typing=True)

        # Initialize narrator
        self.narrator = Narrator()
        self.narrator.add_character_data(character_data)

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
        self.response_area.tag_configure('typing', foreground='darkblue', font=('Arial', 11, 'bold'))

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
        self.submit_btn = tk.Button(
            input_frame,
            text="Send to Narrator",
            command=self.process_input,
            bg='#4CAF50',
            fg='white',
            font=self.input_font
        )
        self.submit_btn.grid(row=2, column=0, sticky="e", pady=(10, 0))

        # Bind Enter key to submit (with Shift+Enter for new line)
        self.user_input.bind('<Return>', self._handle_return_key)
        self.user_input.bind('<Shift-Return>', self._handle_shift_return)

        # Configure grid weights
        input_frame.columnconfigure(0, weight=1)

    def _handle_return_key(self, event):
        """Handle Enter key press - submit the message"""
        self.process_input()
        return "break"  # Prevent default behavior

    def _handle_shift_return(self, event):
        """Handle Shift+Enter - insert new line"""
        return  # Allow default behavior (new line)

    def display_narrator_response(self, message, skip_typing=False):
        """Display narrator response with optional typewriter effect"""
        # Stop any ongoing typing animation
        if self.is_typing and self.current_typing_thread:
            self.is_typing = False
            self.current_typing_thread.join(timeout=0.1)

        if skip_typing:
            # Display immediately without typewriter effect
            self.response_area.config(state='normal')
            self.response_area.insert(tk.END, "Narrator: " + message + "\n\n", 'narrator')
            self.response_area.config(state='disabled')
            self.response_area.see(tk.END)
        else:
            # Start new typing animation in a separate thread
            self.current_typing_thread = threading.Thread(
                target=self._typewriter_effect,
                args=(message,)
            )
            self.current_typing_thread.daemon = True
            self.current_typing_thread.start()

    def _typewriter_effect(self, message):
        """Display text character by character with typewriter effect"""
        self.is_typing = True

        # Store the starting position for this message
        self.root.after(0, self._prepare_typing_area)

        # Calculate typing speed
        base_delay = 0.03  # Base delay in seconds
        # Adjust speed based on message length
        delay = max(0.01, base_delay - (len(message) * 0.00005))

        # Type out the message character by character
        displayed_text = ""
        for char in message:
            if not self.is_typing:
                break

            displayed_text += char
            # Update the text area in the main thread
            self.root.after(0, self._update_displayed_text, displayed_text)
            time.sleep(delay)

        # Final update to ensure complete message is displayed
        if self.is_typing:
            self.root.after(0, self._finalize_message, displayed_text)

        self.is_typing = False

    def _prepare_typing_area(self):
        """Prepare the text area for typing animation"""
        self.response_area.config(state='normal')
        # Insert narrator label and remember the position
        self.response_area.insert(tk.END, "Narrator: ", 'narrator')
        self.typing_position = self.response_area.index("end-1c")
        self.response_area.config(state='disabled')
        self.response_area.see(tk.END)

    def _update_displayed_text(self, text):
        """Update the displayed text in the main thread"""
        if not self.typing_position:
            return

        self.response_area.config(state='normal')
        # Delete only the typing text (from typing position to end)
        self.response_area.delete(self.typing_position, tk.END)
        # Insert current typing progress
        self.response_area.insert(self.typing_position, text, 'typing')
        self.response_area.config(state='disabled')
        self.response_area.see(tk.END)

    def _finalize_message(self, full_text):
        """Finalize the message display after typing is complete"""
        if not self.typing_position:
            return

        self.response_area.config(state='normal')
        # Replace the typing text with final narrator text
        self.response_area.delete(self.typing_position, tk.END)
        self.response_area.insert(self.typing_position, full_text + "\n\n", 'narrator')
        self.response_area.config(state='disabled')
        self.response_area.see(tk.END)
        self.typing_position = None  # Reset typing position

    def process_input(self):
        # Get user input and clear the input box FIRST
        user_text = self.user_input.get("1.0", tk.END).strip()

        # Clear input box immediately
        self.user_input.delete("1.0", tk.END)

        if not user_text:
            return

        # Disable input while processing
        self.submit_btn.config(state='disabled')
        self.user_input.config(state='disabled')

        # Display user message in response area
        self.response_area.config(state='normal')
        self.response_area.insert(tk.END, f"You: " + user_text + "\n", 'user')
        self.response_area.config(state='disabled')
        self.response_area.see(tk.END)

        # Process the input and generate narrator response in a separate thread
        processing_thread = threading.Thread(target=self._generate_and_display_response, args=(user_text,))
        processing_thread.daemon = True
        processing_thread.start()

    def _generate_and_display_response(self, user_text):
        """Generate response and display it with typewriter effect"""
        try:
            # Generate narrator response
            response = self.narrator.generate_response(user_text)

            # Display with typewriter effect
            self.root.after(0, lambda: self.display_narrator_response(response))

            # Start TTS if enabled
            if self.tts_enabled.get():
                self.narrator.speak(response)

        except Exception as e:
            # Handle any errors during response generation
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            self.root.after(0, lambda: self.display_narrator_response(error_msg, skip_typing=True))

        finally:
            # Re-enable input
            self.root.after(0, self._enable_input)

    def _enable_input(self):
        """Re-enable user input after response is complete"""
        self.submit_btn.config(state='normal')
        self.user_input.config(state='normal')
        self.user_input.focus_set()