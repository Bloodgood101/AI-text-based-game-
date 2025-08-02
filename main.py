import tkinter as tk
from tkinter import ttk, scrolledtext

import AI


def create_main_window():
    root = tk.Tk()
    root.title("Main Menu")
    center_window(root, 800, 600)

    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill='both', padx=20, pady=20)

    title_label = ttk.Label(
        main_frame,
        text="Welcome to Project Posh",
        font=('Helvetica', 24, 'bold')
    )
    title_label.pack(pady=(40, 20))

    open_button = ttk.Button(
        main_frame,
        text="Play?",
        command=lambda: switch_to_character_custom(root),
    )
    open_button.pack(pady=20)

    root.mainloop()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    center_x = int(screen_width/2 - width/2)
    center_y = int(screen_height/2 - height/2)
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
    custom_window.title("Character Customisation")
    center_window(custom_window, 800, 600)

    main_frame = ttk.Frame(custom_window)
    main_frame.pack(expand=True, fill='both', padx=40, pady=20)

    # Title label
    label = ttk.Label(main_frame, text="Character Customisation", font=("Helvetica", 20, 'bold'))
    label.pack(pady=(0, 30))

    name_frame = ttk.Frame(main_frame)
    name_frame.pack(fill='x', pady=(0, 30))

    ttk.Label(name_frame, text="Character Name:", font=('Helvetica', 14)).pack(side='left', padx=(0, 10))
    name_var = tk.StringVar()
    name_entry = ttk.Entry(name_frame, textvariable=name_var, width=30)
    name_entry.pack(side='left', expand=True)
    name_entry.focus()  # Set focus to name field by default

    # Define attribute names in order
    attributes_order = ["Strength", "Luck", "Charisma", "Dexterity", "Intelligence"]

    # Create multiple sliders with their value displays
    slider_settings = [
        {"name": "Strength", "min": 0, "max": 10, "default": 5},
        {"name": "Luck", "min": 0, "max": 10, "default": 5},
        {"name": "Charisma", "min": 0, "max": 10, "default": 5},
        {"name": "Dexterity", "min": 0, "max": 10, "default": 5},
        {"name": "Intelligence", "min": 0, "max": 10, "default": 5}
    ]

    slider_widgets = []

    for setting in slider_settings:
        # Create a frame for each slider-value pair
        slider_frame = ttk.Frame(main_frame)
        slider_frame.pack(fill='x', pady=10)

        # Label for slider name
        name_label = ttk.Label(slider_frame, text=setting["name"] + ":", width=12)
        name_label.pack(side='left', padx=(0, 10))

        # Slider widget
        slider = ttk.Scale(
            slider_frame,
            from_=setting["min"],
            to=setting["max"],
            orient='horizontal',
            length=300
        )
        slider.set(setting["default"])
        slider.pack(side='left', expand=True)

        # Value display on the right
        value_frame = ttk.Frame(slider_frame)
        value_frame.pack(side='right', padx=(10, 0))

        ttk.Label(value_frame, text="Value:").pack(side='left')
        value_display = ttk.Label(value_frame, text=str(setting["default"]), width=4)
        value_display.pack(side='left')

        # Configure callback
        slider.config(command=lambda v, d=value_display: d.config(text=f"{float(v):.0f}"))

        slider_widgets.append((slider, value_display))

    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.pack(side='bottom', fill='x', pady=(20, 0))

    close_button = ttk.Button(bottom_frame, text="Exit", command=custom_window.destroy)
    close_button.pack(pady=20)

    next_button = ttk.Button(
        bottom_frame,
        text="Next",
        command=lambda: proceed_to_story(custom_window, name_var, slider_widgets, attributes_order)
    )
    next_button.pack(pady=20)

    custom_window.mainloop()

def proceed_to_story(window, name_var, slider_widgets, attributes_order):
    character_data = collect_character_data(name_var, slider_widgets, attributes_order)
    window.destroy()
    open_prelim_prompt(character_data)

def switch_to_prelim_story(current_window):
    current_window.destroy()
    open_prelim_prompt()

def open_prelim_prompt(character_data):
    window = tk.Tk()
    window.title("Write your story...")
    center_window(window, 800, 600)

    main_frame = ttk.Frame(window)
    main_frame.pack(expand=True, fill='both', padx=20, pady=20)

    # Title label
    title_label = ttk.Label(
        main_frame,
        text="Enter Your Story...",
        font=('Helvetica', 22, 'bold')
    )
    title_label.pack(pady=(0, 20))

    # Large text box with scrollbars
    prompt_label = ttk.Label(main_frame, text="Type below:", font=('Helvetica', 16))
    prompt_label.pack(anchor='w', pady=(0, 5))

    text_box = scrolledtext.ScrolledText(
        main_frame,
        wrap=tk.WORD,  # Wrap at word boundaries
        width=80,  # Width in characters
        height=20,  # Height in lines
        font=('Helvetica', 12),
        padx=10,
        pady=10
    )
    text_box.pack(expand=True, fill='both')
    text_box.focus_set()  # Set focus to text box by default

    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(side='bottom', fill='x', pady=(20, 0))

    # Submit button
    submit_button = ttk.Button(
        button_frame,
        text="Start...",
        command=lambda: process_prompt(text_box.get("1.0", tk.END), character_data, window)
    )
    submit_button.pack(side='left', padx=(0, 10))

    # Clear button
    clear_button = ttk.Button(
        button_frame,
        text="Clear",
        command=lambda: text_box.delete("1.0", tk.END)
    )
    clear_button.pack(side='left')


def process_prompt(prompt_text, character_data, window):
    """Handle the submitted prompt text"""
    cleaned_prompt = prompt_text.strip()
    if not cleaned_prompt:
        print("Please enter a prompt!")
        return

    character_data["story_prompt"] = cleaned_prompt

    # Store in knowledge base
    AI.add_character_data(character_data)

    print("\nCharacter data stored:")
    print(f"Name: {character_data['name']}")
    print("Attributes:")
    for attr, value in character_data["attributes"].items():
        print(f"  {attr}: {value}")
    print(f"Story Prompt: {character_data['story_prompt'][:50]}...")

    print("\nSubmitted Prompt:")
    print(cleaned_prompt)
    # Here you would add your processing logic
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