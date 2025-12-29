import random
import tkinter as tk
from tkinter import scrolledtext
import threading
import time

from AI import Narrator


class ChatApplication:
    def __init__(self, root, character_data):
        self.root = root
        self.character_data = character_data

        # Window configuration with LOTR theme
        self.root.title("The Tale of " + character_data['name'])
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.configure(bg="#1c1c1c")  # Dark background

        # Set up LOTR fonts
        self.title_font = ("Cinzel", 16, "bold")
        self.header_font = ("Cinzel", 12, "bold")
        self.body_font = ("Georgia", 11)
        self.input_font = ("Georgia", 10)

        # Title label
        title_label = tk.Label(
            root,
            text="The Chronicles of " + character_data['name'],
            font=self.title_font,
            bg="#1c1c1c",
            fg="#d4af37",
            pady=10
        )
        title_label.grid(row=0, column=0, sticky="ew")

        # Toggle and state variables
        self.tts_enabled = tk.BooleanVar(value=False)
        self.is_typing = False
        self.current_typing_thread = None
        self.typing_position = None
        self.fight_counter = 0  # For increasing stats

        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Main content area
        self.root.rowconfigure(2, weight=0)  # Input area

        # Create narrator response section
        self.create_response_section()

        # Create user input section
        self.create_input_section()

        # Sample initial message with LOTR flavor
        welcome_msg = (
            f"Hail, {character_data['name']}! I am the chronicler of your tale.\n"
            f"Your story begins thus: {character_data['story_prompt'][:500]}...\n"
            f"May the stars guide your path."
        )
        self.display_narrator_response(welcome_msg, skip_typing=True)

        # Initialize narrator
        self.narrator = Narrator()
        self.narrator.add_character_data(character_data)

        # Install exception handler
        threading.excepthook = self.thread_exception_handler

    def thread_exception_handler(self, args):
        """Handle uncaught exceptions in threads"""
        print(f"Thread exception: {args.exc_type.__name__}: {args.exc_value}")
        # Don't crash on Tkinter main loop errors
        if "main loop" in str(args.exc_value):
            return

    def create_response_section(self):
        # Response frame with LOTR styling
        response_frame = tk.LabelFrame(
            self.root,
            text="Chronicles of the Quest",
            font=self.header_font,
            bg="#1c1c1c",
            fg="#d4af37",
            relief="ridge",
            bd=4
        )
        response_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        # Scrolled Text widget for responses with parchment-like appearance
        self.response_area = scrolledtext.ScrolledText(
            response_frame,
            wrap=tk.WORD,
            font=self.body_font,
            state='disabled',
            padx=15,
            pady=15,
            bg="#2a2a2a",
            fg="#e6d5a8",
            insertbackground="#d4af37",
            relief="sunken",
            bd=3
        )
        self.response_area.grid(row=0, column=0, sticky="nsew")

        # Configure tags for different message types
        self.response_area.tag_configure(
            'narrator',
            foreground="#d4af37",
            font=("Cinzel", 11, "italic"),
            lmargin1=15,
            lmargin2=15,
            rmargin=15
        )
        self.response_area.tag_configure(
            'user',
            foreground="#8da1a1",
            font=("Georgia", 11),
            lmargin1=15,
            lmargin2=15,
            rmargin=15
        )
        self.response_area.tag_configure(
            'typing',
            foreground="#ffcc5c",
            font=("Cinzel", 11, "bold italic")
        )

    def create_input_section(self):
        # Input frame with dark background
        input_frame = tk.Frame(self.root, bg="#1c1c1c")
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Prompt label with LOTR styling
        tk.Label(
            input_frame,
            text="Speak, traveler (use @ for commands like @stats):",
            font=self.header_font,
            bg="#1c1c1c",
            fg="#8da1a1"
        ).grid(row=0, column=0, sticky="w")

        # Text widget for user input with medieval styling
        self.user_input = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            font=self.input_font,
            padx=12,
            pady=12,
            bg="#3a3a3a",
            fg="#f0e6d2",
            insertbackground="#d4af37",
            relief="groove",
            bd=3
        )
        self.user_input.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.user_input.focus_set()

        # Submit button styled as ancient scroll/button
        self.submit_btn = tk.Button(
            input_frame,
            text="Send to the Narrator",
            command=self.process_input,
            bg="#5d4c2e",
            fg="#f0e6d2",
            activebackground="#8b7355",
            activeforeground="#ffffff",
            font=("Cinzel", 10, "bold"),
            relief="raised",
            bd=3,
            padx=20,
            pady=6
        )
        self.submit_btn.grid(row=2, column=0, sticky="e", pady=(12, 0))

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
        attributes_list = ["dexterity", "strength", "luck", "charisma", "intelligence"]

        try:
            # Check if Tkinter main loop is still running
            if not hasattr(self.root, 'tk') or not self.root.winfo_exists():
                return

            # Check for @ commands
            if user_text.startswith("@"):
                command = user_text[1:].lower().strip()

                # @stats command
                if command == "stats" or command == "attributes":
                    response = self.get_stats()
                    # Use safe wrapper
                    if self.root.winfo_exists():
                        self.root.after(0, lambda: self.display_narrator_response(response))

                # @attribute battle commands
                elif any(attribute in command for attribute in attributes_list):
                    response = self.handle_attribute_battle(command, attributes_list)
                    if self.root.winfo_exists():
                        self.root.after(0, lambda: self.display_narrator_response(response))

                # Unknown @ command
                else:
                    response = f"I do not understand the command '@{command}'. Try '@stats' or use an attribute like '@strength'."
                    if self.root.winfo_exists():
                        self.root.after(0, lambda: self.display_narrator_response(response))

            # Normal chat (without @ prefix)
            else:
                # Generate narrator response
                response = self.narrator.generate_response(user_text)
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.display_narrator_response(response))

                    # Start TTS if enabled
                    if self.tts_enabled.get() and self.root.winfo_exists():
                        self.narrator.speak(response)

        except RuntimeError as e:
            if "main loop" not in str(e):  # Only log if it's not the expected error
                print(f"Runtime error: {e}")
            return  # Silently ignore main loop errors
        except Exception as e:
            # Handle any errors during response generation
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.display_narrator_response(error_msg, skip_typing=True))
        finally:
            # Re-enable input if window still exists
            if self.root.winfo_exists():
                self.root.after(0, self._enable_input)

    def get_stats(self):
        stats = [f"Character: {self.character_data['name']}", "Attributes:"]
        for attribute, value in self.character_data['attributes'].items():
            stats.append(f"    {attribute}:{value}")
        return "\n".join(stats)

    def handle_attribute_battle(self, command, attributes_list):
        self.fight_counter += 1
        print(self.fight_counter)
        print("attribute battle triggered...")

        mentioned_attributes = []

        for attribute in attributes_list:
            if attribute in command:
                mentioned_attributes.append(attribute)
        character_attributes = self.character_data['attributes']
        # For levelling up mechanic
        if self.fight_counter % random.randint(2, 8) == 0:
            attribute_upgrade = random.choice(attributes_list)
            value = character_attributes.get(attribute_upgrade, 0)
            self.character_data[attribute_upgrade] = value + 1

            level_up = f"Your {attribute_upgrade} has increased by 1 through sheer prowess..."
        else:
            level_up = ""

        if mentioned_attributes:
            response = [f"You have decided to use {mentioned_attributes} to solve this problem...\n"]
            score = 0
            for attribute in mentioned_attributes:
                attribute_value = character_attributes.get(attribute, 0)
                print(f"Your attribute score is: {attribute_value}")
                score += attribute_value
            enemy_score = 0
            for i in range(len(mentioned_attributes)):
                enemy_score += random.randint(1, 10)
                print(f"Enemy score is: {enemy_score}")

            if score >= enemy_score:
                response.append(f"Your {mentioned_attributes} outclassed the enemy!\n")
                response.append(f"\n{score} > {enemy_score}\n")
            else:
                response.append(f"Your {mentioned_attributes} can not match up against this monster...\n")
                response.append(f"\n{score} < {enemy_score}\n")
            if level_up:
                response.append(level_up)
            return response

    def _enable_input(self):
        """Re-enable user input after response is complete"""
        self.submit_btn.config(state='normal')
        self.user_input.config(state='normal')
        self.user_input.focus_set()