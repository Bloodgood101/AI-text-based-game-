import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import datetime
import os

from AI import Narrator

# LOTR Color Scheme
DARK_BG = "#1c1c1c"
PARCHMENT_BG = "#2a2a2a"
PARCHMENT_TEXT = "#e6d5a8"
GOLD_ACCENT = "#d4af37"
MUTED_SILVER = "#8da1a1"
LEATHER_BROWN = "#5d4c2e"
DARK_INPUT_BG = "#3a3a3a"

# LOTR Fonts (fallback to standard fonts if not available)
LOTR_FONTS = {
    "title": ("Cinzel", 24, "bold"),
    "header": ("Cinzel", 16, "bold"),
    "subheader": ("Cinzel", 14),
    "body": ("Georgia", 12),
    "input": ("Georgia", 11)
}


def create_main_window():
    root = tk.Tk()
    root.title("Unspoken Chronicles")
    root.configure(bg=DARK_BG)
    center_window(root, 900, 700)

    # Main container with LOTR styling
    main_frame = tk.Frame(root, bg=DARK_BG, relief="ridge", bd=4)
    main_frame.pack(expand=True, fill='both', padx=40, pady=40)

    # Title with LOTR styling, wanted LOTR styling for effect
    title_label = tk.Label(
        main_frame,
        text="Unspoken Chronicles",
        font=LOTR_FONTS["title"],
        bg=DARK_BG,
        fg=GOLD_ACCENT,
        pady=20
    )
    title_label.pack(pady=(40, 40))

    # Subtitle
    subtitle_label = tk.Label(
        main_frame,
        text="Begin Your Journey",
        font=LOTR_FONTS["subheader"],
        bg=DARK_BG,
        fg=MUTED_SILVER
    )
    subtitle_label.pack(pady=(0, 60))

    # Play button with medieval styling
    open_button = tk.Button(
        main_frame,
        text="Begin Your Tale",
        command=lambda: switch_to_character_custom(root),
        bg=LEATHER_BROWN,
        fg=PARCHMENT_TEXT,
        activebackground="#8b7355",
        activeforeground="#ffffff",
        font=LOTR_FONTS["header"],
        relief="raised",
        bd=4,
        padx=30,
        pady=15,
        cursor="hand2"
    )
    open_button.pack(pady=30)

    # Divider line
    divider = tk.Frame(main_frame, height=2, bg=GOLD_ACCENT)
    divider.pack(fill='x', pady=40)

    # Model status with themed styling
    model_status = check_model_status()
    status_label = tk.Label(
        main_frame,
        text=model_status,
        font=LOTR_FONTS["body"],
        bg=DARK_BG,
        fg='#7cfc00' if 'Ready' in model_status else '#ff6b6b'
    )
    status_label.pack(pady=10)

    # Footer text
    footer_label = tk.Label(
        main_frame,
        text="May the Gods guide your path",
        font=("Georgia", 10, "italic"),
        bg=DARK_BG,
        fg=MUTED_SILVER
    )
    footer_label.pack(side='bottom', pady=20)

    root.mainloop()


def check_model_status():
    model_path = "./models/llama-2-7b-chat.Q4_0.gguf"
    if os.path.exists(model_path):
        return "Seer: Ready to weave your fate"
    else:
        return "Seer: Scroll of knowledge not found"


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width / 2 - width / 2)
    center_y = int(screen_height / 2 - height / 2)
    window.geometry(f'{width}x{height}+{center_x}+{center_y}')


def switch_to_character_custom(current_window):
    current_window.destroy()
    open_character_custom()


def collect_character_data(name_var, slider_widgets, attributes_order):
    character_data = {
        "name": name_var.get(),
        "attributes": {}
    }

    for i, attr_name in enumerate(attributes_order):
        slider = slider_widgets[i][0]
        value = int(float(slider.get()))
        character_data["attributes"][attr_name] = value
    return character_data


def open_character_custom():
    custom_window = tk.Tk()
    custom_window.title("Forge Your Hero")
    custom_window.configure(bg=DARK_BG)
    center_window(custom_window, 900, 700)

    # Main container
    main_frame = tk.Frame(custom_window, bg=DARK_BG, relief="ridge", bd=4)
    main_frame.pack(expand=True, fill='both', padx=40, pady=30)

    # Title with LOTR styling
    title_label = tk.Label(
        main_frame,
        text="Forge Your Hero",
        font=LOTR_FONTS["title"],
        bg=DARK_BG,
        fg=GOLD_ACCENT,
        pady=10
    )
    title_label.pack(pady=(0, 30))

    # Name entry section
    name_frame = tk.Frame(main_frame, bg=DARK_BG)
    name_frame.pack(fill='x', pady=(0, 30))

    name_label = tk.Label(
        name_frame,
        text="Hero's Name:",
        font=LOTR_FONTS["header"],
        bg=DARK_BG,
        fg=MUTED_SILVER
    )
    name_label.pack(side='left', padx=(0, 15))

    name_var = tk.StringVar()
    name_entry = tk.Entry(
        name_frame,
        textvariable=name_var,
        width=30,
        font=LOTR_FONTS["input"],
        bg=DARK_INPUT_BG,
        fg=PARCHMENT_TEXT,
        insertbackground=GOLD_ACCENT,
        relief="groove",
        bd=2
    )
    name_entry.pack(side='left', expand=True)
    name_entry.focus()

    # Attributes frame
    attributes_frame = tk.LabelFrame(
        main_frame,
        text="Allot Your Virtues",
        font=LOTR_FONTS["subheader"],
        bg=DARK_BG,
        fg=GOLD_ACCENT,
        relief="groove",
        bd=3
    )
    attributes_frame.pack(fill='both', expand=True, pady=(0, 30))

    # Define attribute names and their LOTR-style descriptions
    attribute_descriptions = {
        "strength": "Strength",
        "luck": "Luck",
        "charisma": "Charisma",
        "dexterity": "Dexterity",
        "intelligence": "Intelligence"
    }
    attributes_order = ["strength", "luck", "charisma", "dexterity", "intelligence"]

    slider_widgets = []

    for attr in attributes_order:
        # Create a frame for each slider
        slider_frame = tk.Frame(attributes_frame, bg=DARK_BG)
        slider_frame.pack(fill='x', pady=12, padx=20)

        # Attribute name and description
        name_label = tk.Label(
            slider_frame,
            text=f"{attribute_descriptions[attr]}:",
            font=LOTR_FONTS["body"],
            bg=DARK_BG,
            fg=MUTED_SILVER,
            width=20,
            anchor='w'
        )
        name_label.pack(side='left', padx=(0, 20))

        # Slider
        slider = tk.Scale(
            slider_frame,
            from_=0,
            to=10,
            orient='horizontal',
            length=400,
            bg=DARK_BG,
            fg=PARCHMENT_TEXT,
            troughcolor=PARCHMENT_BG,
            highlightthickness=0,
            font=LOTR_FONTS["body"],
            sliderrelief="raised",
            bd=3
        )
        slider.set(5)
        slider.pack(side='left', expand=True)

        # Value display
        value_frame = tk.Frame(slider_frame, bg=DARK_BG)
        value_frame.pack(side='right', padx=(20, 0))

        value_label = tk.Label(
            value_frame,
            text="Valor:",
            font=LOTR_FONTS["body"],
            bg=DARK_BG,
            fg=MUTED_SILVER
        )
        value_label.pack(side='left')

        value_display = tk.Label(
            value_frame,
            text="5",
            font=LOTR_FONTS["body"],
            bg=DARK_BG,
            fg=GOLD_ACCENT,
            width=4,
            relief="sunken",
            bd=2
        )
        value_display.pack(side='left', padx=(5, 0))

        # Configure callback
        slider.config(command=lambda v, d=value_display: d.config(text=f"{float(v):.0f}"))

        slider_widgets.append((slider, value_display))

    # Button frame
    bottom_frame = tk.Frame(main_frame, bg=DARK_BG)
    bottom_frame.pack(side='bottom', fill='x', pady=(20, 0))

    # Close button
    close_button = tk.Button(
        bottom_frame,
        text="← Return to Hall",
        command=custom_window.destroy,
        bg=LEATHER_BROWN,
        fg=PARCHMENT_TEXT,
        font=LOTR_FONTS["body"],
        relief="raised",
        bd=3,
        padx=20,
        pady=8
    )
    close_button.pack(side='left', padx=(0, 20))

    # Next button
    next_button = tk.Button(
        bottom_frame,
        text="Continue Your Saga →",
        command=lambda: proceed_to_story(custom_window, name_var, slider_widgets, attributes_order),
        bg=GOLD_ACCENT,
        fg=DARK_BG,
        font=LOTR_FONTS["header"],
        relief="raised",
        bd=4,
        padx=30,
        pady=10,
        cursor="hand2"
    )
    next_button.pack(side='right')

    custom_window.mainloop()


def proceed_to_story(window, name_var, slider_widgets, attributes_order):
    character_data = collect_character_data(name_var, slider_widgets, attributes_order)
    window.destroy()
    open_prelim_prompt(character_data)


def open_prelim_prompt(character_data):
    window = tk.Tk()
    window.title("Chronicle Your Quest")
    window.configure(bg=DARK_BG)
    center_window(window, 900, 750)

    # Main container
    main_frame = tk.Frame(window, bg=DARK_BG, relief="ridge", bd=4)
    main_frame.pack(expand=True, fill='both', padx=40, pady=30)

    # Title with LOTR styling
    title_label = tk.Label(
        main_frame,
        text="Chronicle Your Quest",
        font=LOTR_FONTS["title"],
        bg=DARK_BG,
        fg=GOLD_ACCENT,
        pady=10
    )
    title_label.pack(pady=(0, 20))

    # Hero's name display
    hero_frame = tk.Frame(main_frame, bg=DARK_BG)
    hero_frame.pack(fill='x', pady=(0, 20))

    hero_label = tk.Label(
        hero_frame,
        text=f"Hero: {character_data['name']}",
        font=LOTR_FONTS["header"],
        bg=DARK_BG,
        fg=MUTED_SILVER
    )
    hero_label.pack()

    #introduce setting mechanic (now the AI knows what universe you are in)
    topic_frame = tk.Frame(main_frame, bg=DARK_BG)
    topic_frame.pack(fill="x", pady=(0,15))

    topic_label = tk.Label(
        topic_frame,
        text="Realm/Setting:",
        font=LOTR_FONTS["subheader"],
        bg=DARK_BG,
        fg=MUTED_SILVER
    )
    topic_label.pack(anchor='w', pady=(0, 5))

    topic_var = tk.StringVar()
    topic_entry = tk.Entry(
        topic_frame,
        textvariable=topic_var,
        width=60,
        font=LOTR_FONTS["input"],
        bg=DARK_INPUT_BG,
        fg=PARCHMENT_TEXT,
        insertbackground=GOLD_ACCENT,
        relief="groove",
        bd=2
    )
    topic_entry.pack(fill='x', pady=(0, 10))

    # Text box with LOTR styling
    text_frame = tk.LabelFrame(
        main_frame,
        text="Scroll of Beginnings",
        font=LOTR_FONTS["subheader"],
        bg=DARK_BG,
        fg=GOLD_ACCENT,
        relief="groove",
        bd=3
    )
    text_frame.pack(expand=True, fill='both', pady=(0, 20))
    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    text_box = scrolledtext.ScrolledText(
        text_frame,
        wrap=tk.WORD,
        font=LOTR_FONTS["input"],
        bg=PARCHMENT_BG,
        fg=PARCHMENT_TEXT,
        insertbackground=GOLD_ACCENT,
        relief="flat",
        bd=0,
        padx=15,
        pady=15
    )
    text_box.grid(row=0, column=0, sticky="nsew")
    text_box.focus_set()

    # Sample story prompt (optional hint)
    sample_prompt = "The stars were strange in the sky the night the elves first spoke your name..."
    text_box.insert("1.0", sample_prompt)

    # Button frame
    button_frame = tk.Frame(main_frame, bg=DARK_BG)
    button_frame.pack(side='bottom', fill='x', pady=(10, 0))

    # Clear button
    clear_button = tk.Button(
        button_frame,
        text="Clear Scroll",
        command=lambda: text_box.delete("1.0", tk.END),
        bg=LEATHER_BROWN,
        fg=PARCHMENT_TEXT,
        font=LOTR_FONTS["body"],
        relief="raised",
        bd=3,
        padx=20,
        pady=8
    )
    clear_button.pack(side='left')

    # Submit button
    submit_button = tk.Button(
        button_frame,
        text="Begin Your Legend️",
        command=lambda: process_prompt(text_box.get("1.0", tk.END), topic_var.get(), character_data, window),
        bg=GOLD_ACCENT,
        fg=DARK_BG,
        font=LOTR_FONTS["header"],
        relief="raised",
        bd=4,
        padx=30,
        pady=10,
        cursor="hand2"
    )
    submit_button.pack(side='right')

    window.mainloop()


def process_prompt(prompt_text, topic, character_data, window):
    """Handle the submitted prompt text"""
    cleaned_prompt = prompt_text.strip()
    cleaned_topic = topic.strip()
    if not cleaned_prompt:
        # Create error popup with LOTR styling
        error_window = tk.Toplevel(window)
        error_window.title("Empty Scroll")
        error_window.configure(bg=DARK_BG)
        error_window.geometry("400x200")
        error_window.resizable(False, False)

        center_window(error_window, 400, 200)

        error_label = tk.Label(
            error_window,
            text="The scroll cannot be empty!\n\nInscribe your tale, brave adventurer.",
            font=LOTR_FONTS["body"],
            bg=DARK_BG,
            fg="#ff6b6b",
            wraplength=350,
            justify="center",
            pady=20
        )
        error_label.pack(expand=True)

        ok_button = tk.Button(
            error_window,
            text="I Understand",
            command=error_window.destroy,
            bg=LEATHER_BROWN,
            fg=PARCHMENT_TEXT,
            font=LOTR_FONTS["body"],
            relief="raised",
            bd=3,
            padx=20,
            pady=8
        )
        ok_button.pack(pady=20)

        return

    character_data["setting"] = cleaned_topic
    character_data["story_prompt"] = cleaned_prompt

    # Log the character creation
    log_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "character_data": character_data
    }

    try:
        with open("character_creation_log.json", "w", encoding="utf-8") as f:
            f.truncate(0) #did the same for the gameLog.txt need to clear data for each playthrough for training data
            f.seek(0)
            f.write(json.dumps(log_data, indent=2) + "\n")
    except Exception as e:
        print(f"Error saving log: {e}")

    print("\nScroll Created:")
    print(f"Name: {character_data['name']}")
    print(f"Setting: {character_data.get('setting', 'Not specified')}")
    print("⚜Virtues:")
    for attr, value in character_data["attributes"].items():
        print(f"   {attr.capitalize()}: {value}")
    print(f"Tale: {character_data['story_prompt'][:100]}...")

    window.destroy()
    launch_game(character_data)


def launch_game(character_data):
    """Create and start the game window"""
    root = tk.Tk()
    from Game import ChatApplication
    ChatApplication(root, character_data)
    root.mainloop()


if __name__ == "__main__":
    create_main_window()