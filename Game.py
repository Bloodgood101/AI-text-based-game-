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

        # Current interaction type
        self.current_interaction_type = "speak"  # Default: speak

        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)  # Main content area
        self.root.rowconfigure(2, weight=0)  # Input area

        # Create narrator response section
        self.create_response_section()

        # Create user input section
        self.create_input_section()

        # Create interaction type selector (speak, do, action)
        self.create_interaction_selector()

        self.last_narrator_response = ""  # for empty inputs

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

    def create_interaction_selector(self):
        """Create buttons for selecting interaction type"""
        interaction_frame = tk.LabelFrame(
            self.root,
            text="Choose Your Action",
            font=self.header_font,
            bg="#1c1c1c",
            fg="#d4af37",
            relief="ridge",
            bd=4,
            padx=10,
            pady=10
        )
        interaction_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # Interaction type buttons
        self.speak_btn = tk.Radiobutton(
            interaction_frame,
            text="Speak",
            variable=tk.StringVar(value="speak"),  # Will be set properly below
            value="speak",
            command=lambda: self.set_interaction_type("speak"),
            bg="#2a4d2a",
            fg="#f0e6d2",
            activebackground="#3a6d3a",
            activeforeground="#ffffff",
            selectcolor="#1c1c1c",
            font=("Cinzel", 10, "bold"),
            indicatoron=0,
            width=15,
            height=2,
            relief="raised",
            bd=3
        )
        self.speak_btn.pack(pady=5, fill='x')

        self.do_btn = tk.Radiobutton(
            interaction_frame,
            text="Do",
            variable=tk.StringVar(value="do"),
            value="do",
            command=lambda: self.set_interaction_type("do"),
            bg="#4d2a2a",
            fg="#f0e6d2",
            activebackground="#6d3a3a",
            activeforeground="#ffffff",
            selectcolor="#1c1c1c",
            font=("Cinzel", 10, "bold"),
            indicatoron=0,
            width=15,
            height=2,
            relief="raised",
            bd=3
        )
        self.do_btn.pack(pady=5, fill='x')

        self.action_btn = tk.Radiobutton(
            interaction_frame,
            text="Action",
            variable=tk.StringVar(value="action"),
            value="action",
            command=lambda: self.set_interaction_type("action"),
            bg="#2a2a4d",
            fg="#f0e6d2",
            activebackground="#3a3a6d",
            activeforeground="#ffffff",
            selectcolor="#1c1c1c",
            font=("Cinzel", 10, "bold"),
            indicatoron=0,
            width=15,
            height=2,
            relief="raised",
            bd=3
        )
        self.action_btn.pack(pady=5, fill='x')

        # Stats button
        self.stats_btn = tk.Button(
            interaction_frame,
            text="📊 Stats",
            command=self.show_stats,
            bg="#5d4c2e",
            fg="#f0e6d2",
            activebackground="#8b7355",
            activeforeground="#ffffff",
            font=("Cinzel", 10, "bold"),
            relief="raised",
            bd=3,
            width=15,
            height=2
        )
        self.stats_btn.pack(pady=20, fill='x')

        # Selected interaction indicator
        self.interaction_label = tk.Label(
            interaction_frame,
            text="Current: Speak",
            font=("Georgia", 14, "bold"),
            bg="#1c1c1c",
            fg="#d4af37",
            pady=5
        )
        self.interaction_label.pack(fill='x')

        # Set initial selection
        self.set_interaction_type("speak")

    def set_interaction_type(self, interaction_type):
        """Set the current interaction type"""
        self.current_interaction_type = interaction_type

        # Update UI to show current selection
        self.interaction_label.config(text=f"Current: {interaction_type.capitalize()}")

        # Update button states (visual feedback)
        for btn in [self.speak_btn, self.do_btn, self.action_btn]:
            btn.config(relief="raised")

        if interaction_type == "speak":
            self.speak_btn.config(relief="sunken")
            self.user_input.delete("1.0", tk.END)
            self.user_input.insert("1.0", "What do you say? ")
        elif interaction_type == "do":
            self.do_btn.config(relief="sunken")
            self.user_input.delete("1.0", tk.END)
            self.user_input.insert("1.0", "What do you do? ")
        elif interaction_type == "action":
            self.action_btn.config(relief="sunken")
            self.user_input.delete("1.0", tk.END)
            self.user_input.insert("1.0", "Which attribute do you use? ")

    def create_input_section(self):
        # Input frame with dark background
        input_frame = tk.Frame(self.root, bg="#1c1c1c")
        input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Prompt label with LOTR styling
        tk.Label(
            input_frame,
            text="Choose, traveler:",
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
        self.last_narrator_response = message #for null user input
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

        #check if the user box is empty, or still has the default text
        is_empty = not user_text or user_text in [
            "What do you say? ",
            "What do you do? ",
            "Which attribute do you use? "
        ]

        if is_empty and self.last_narrator_response:
            user_text = f"[CONTINUE] {self.last_narrator_response[:200]}..."

            #Display notice in the main chat
            self.response_area.config(state='normal')
            self.response_area.insert(
                tk.END,
                "You: [CONTINUE]"
            )
            self.response_area.config(state='disabled')
            self.response_area.see(tk.END)
        elif is_empty:
            #if there is no data help off just return nothing
            return

        # Disable input while processing
        self.submit_btn.config(state='disabled')
        self.user_input.config(state='disabled')

        # Display user message in response area with interaction type prefix
        if not is_empty:
            interaction_prefix = f"[{self.current_interaction_type.upper()}] "
            self.response_area.config(state='normal')
            self.response_area.insert(tk.END, f"You {interaction_prefix}: " + user_text + "\n", 'user')
            self.response_area.config(state='disabled')
            self.response_area.see(tk.END)

        # Process the input and generate narrator response in a separate thread
        processing_thread = threading.Thread(
            target=self._generate_and_display_response,
            args=(user_text, self.current_interaction_type)
        )
        processing_thread.daemon = True
        processing_thread.start()

    def _generate_and_display_response(self, user_text, interaction_type):
        """Generate response and display it with typewriter effect"""
        attributes_list = ["dexterity", "strength", "luck", "charisma", "intelligence"]

        try:
            # Check if Tkinter main loop is still running
            if not hasattr(self.root, 'tk') or not self.root.winfo_exists():
                return

            # Handle based on interaction type
            if interaction_type == "speak":
                # Normal chat - generate narrator response for dialogue
                response = self.narrator.generate_response(f"[SPEAK] {user_text}")
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.display_narrator_response(response))

            elif interaction_type == "do":
                # Action description - treat as physical action
                response = self.narrator.generate_response(f"[DO ACTION] {user_text}")
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.display_narrator_response(response))

            elif interaction_type == "action":
                # Attribute-based action - similar to old @attribute system
                response = self.handle_attribute_action(user_text, attributes_list)
                if self.root.winfo_exists():
                    self.root.after(0, lambda: self.display_narrator_response(response))

            # Start TTS if enabled
            if self.tts_enabled.get() and self.root.winfo_exists() and interaction_type != "action":
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

    def show_stats(self):
        """Display character stats"""
        response = self.get_stats()
        self.display_narrator_response(response, skip_typing=True)

    def get_stats(self):
        stats = [f"Character: {self.character_data['name']}", "Attributes:"]
        for attribute, value in self.character_data['attributes'].items():
            stats.append(f"    {attribute}: {value}")
        return "\n".join(stats)

    def handle_attribute_action(self, user_text, attributes_list):
        """Handle attribute-based actions (replaces @attribute commands)"""
        self.fight_counter += 1
        print(f"Attribute action triggered... (Counter: {self.fight_counter})")

        mentioned_attributes = []

        # Find which attributes are mentioned in the user's text
        for attribute in attributes_list:
            if attribute.lower() in user_text.lower():
                mentioned_attributes.append(attribute)

        character_attributes = self.character_data['attributes']

        # For levelling up mechanic
        level_up = ""
        level_up_attribute = None
        if self.fight_counter % random.randint(2, 8) == 0 and mentioned_attributes:
            level_up_attribute = random.choice(mentioned_attributes)
            value = character_attributes.get(level_up_attribute, 0)
            self.character_data['attributes'][level_up_attribute] = value + 1
            level_up = f"\nYour {level_up_attribute} has increased by 1 through sheer prowess!"

        battle_result = ""
        outcome = "neutral"
        score = 0
        enemy_score = 0

        if mentioned_attributes:
            # Calculate your score
            score = 0
            for attribute in mentioned_attributes:
                attribute_value = character_attributes.get(attribute, 0)
                score += attribute_value

            # Calculate enemy score
            enemy_score = 0
            for i in range(len(mentioned_attributes)):
                enemy_score += random.randint(1, 10)

            # Determine outcome
            if score >= enemy_score:
                battle_result = f"You used your {', '.join(mentioned_attributes)} (score: {score}) and outclassed the challenge (score: {enemy_score})!"
                outcome = "success"
            else:
                battle_result = f"You used your {', '.join(mentioned_attributes)} (score: {score}) but couldn't match up against this challenge (score: {enemy_score})..."
                outcome = "failure"

            # Add flavor text
            if outcome == "success":
                battle_result += f" You succeeded in {user_text.lower()}!"
            else:
                battle_result += f" You failed to {user_text.lower()}."

            # Add level up if applicable
            if level_up:
                battle_result += level_up

            # Now generate a story-based response from the narrator
            # Pass the battle result and outcome to the narrator for story continuation
            prompt_for_narrator = f"[ATTRIBUTE ACTION] I attempted to {user_text.lower()} using my {', '.join(mentioned_attributes)} attributes. {battle_result}"

            # Get narrator's story response
            narrator_response = self.narrator.generate_response(prompt_for_narrator)

            # Combine the battle result with the narrator's story continuation
            full_response = f"{battle_result}\n\n{narrator_response}"

            return full_response
        else:
            # No attributes mentioned
            battle_result = f"You attempt to {user_text.lower()}, but without focusing on any specific attribute, your efforts are unfocused. Try mentioning an attribute like 'strength', 'dexterity', etc."

            # Still get narrator response for story continuity
            prompt_for_narrator = f"[ATTRIBUTE ACTION] I attempted to {user_text.lower()} but my actions were unfocused without using specific attributes."
            narrator_response = self.narrator.generate_response(prompt_for_narrator)

            return f"{battle_result}\n\n{narrator_response}"

    def _enable_input(self):
        """Re-enable user input after response is complete"""
        self.submit_btn.config(state='normal')
        self.user_input.config(state='normal')
        self.user_input.focus_set()

        # Reset input prompt based on current interaction type
        if self.current_interaction_type == "speak":
            self.user_input.insert("1.0", "What do you say? ")
        elif self.current_interaction_type == "do":
            self.user_input.insert("1.0", "What do you do? ")
        elif self.current_interaction_type == "action":
            self.user_input.insert("1.0", "Which attribute do you use? ")