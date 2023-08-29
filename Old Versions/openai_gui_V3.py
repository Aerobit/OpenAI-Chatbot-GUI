import openai
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from ttkthemes import ThemedTk
from tkinter import scrolledtext
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from uuid import getnode as get_mac
from sys import exit
import threading
import time
import json

CONFIG_FILE = 'config.json'
base_key = 'GRO9jNw5lXc4U5B8_Wz3zAaPPhQDgWFQ8CQxnLhxjJ0='
mac = ':'.join(('%012X' % get_mac())[i:i+2] for i in range(0, 12, 2))
hashed_key = hashlib.sha256((mac + base_key).encode()).digest()
SECRET_KEY = base64.urlsafe_b64encode(hashed_key[:32])
cipher = Fernet(SECRET_KEY)

class UserConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self.config_data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_config(self, data):
        with open(self.config_file, 'w') as file:
            json.dump(data, file)

    def process_key(self, api_key):
        return cipher.encrypt(api_key.encode()).decode()

    def reverse_processing(self, processed_key):
        return cipher.decrypt(processed_key.encode()).decode()

    def retrieve_key(self):
        try:
            processed_key = self.config_data.get("api_key")
            return self.reverse_processing(processed_key)
        except (TypeError, AttributeError):
            return None

    def save_key(self, api_key):
        processed_key = self.process_key(api_key)
        self.config_data["api_key"] = processed_key
        self.save_config(self.config_data)

    def retrieve_theme(self):
        return self.config_data.get("theme", "arc")

    def save_theme(self, theme):
        self.config_data["theme"] = theme
        self.save_config(self.config_data)

    def retrieve_model(self):
        return self.config_data.get("model", "gpt-3.5-turbo")

    def save_model(self, model):
        self.config_data["model"] = model
        self.save_config(self.config_data)

    def retrieve_temperature(self):
        return self.config_data.get("temperature", "0.8")

    def save_temperature(self, temperature):
        self.config_data["temperature"] = temperature
        self.save_config(self.config_data)

    def retrieve_max_tokens(self):
        return self.config_data.get("max_tokens", "300")

    def save_max_tokens(self, max_tokens):
        self.config_data["max_tokens"] = max_tokens
        self.save_config(self.config_data)

    def validate_api_key(self, api_key):
        try:
            openai.api_key = api_key
            openai.Completion.create(model="text-davinci-003", prompt="Test", max_tokens=5)
            return True
        except openai.OpenAIError:
            return False

class ChatbotUI:
    def __init__(self):
        self.config_manager = UserConfigManager()
        self.api_key = self.config_manager.retrieve_key()
        if not self.api_key:
            self.api_key_entry_popup()
            self.api_key = self.config_manager.retrieve_key()
        if not self.api_key:
            exit()
        openai.api_key = self.api_key.strip()
        self.current_theme = self.config_manager.retrieve_theme()
        self.current_model = self.config_manager.retrieve_model()
        self.current_temperature = self.config_manager.retrieve_temperature()
        self.current_max_tokens = self.config_manager.retrieve_max_tokens()

        self.root = ThemedTk(theme=self.current_theme)
        self.root.title("Chatbot")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        self.model_var = tk.StringVar(value=self.current_model)
        self.temperature_var = tk.StringVar(value=self.current_temperature)
        self.max_tokens_var = tk.StringVar(value=self.current_max_tokens)

        self.setup_ui()
        self.context_entry.config(width=self.user_input['width'])
        self.messages = [{"role": "system", "content": self.context_entry.get("1.0", tk.END).strip()}]
        self.update_conversation()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_ui(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Change API Key", command=self.api_key_entry_popup)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        self.settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=self.settings_menu)
        self.setup_settings_menu()

        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=self.view_menu)
        self.setup_theme_menu()

        self.root.config(menu=menubar)

        self.root.grid_rowconfigure(4, weight=5)
        self.root.grid_columnconfigure(0, weight=5)

        for i in [0, 1, 2, 3, 6]:
            self.root.grid_rowconfigure(i, weight=1)

        self.context_entry = tk.Text(self.root, height=3)
        self.context_entry.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=(10, 10), pady=(0, 10))
        self.context_entry.insert(tk.END, "You are a helpful assistant.")
        
        self.conversation = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.conversation.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=4, sticky="ew", padx=10)

        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        self.user_input = tk.Text(input_frame, height=3, width=50, wrap=tk.WORD)
        self.user_input.grid(row=0, column=0, sticky="nsew")
        self.user_input.bind("<Return>", self.send_message_on_enter)
        input_frame.grid_columnconfigure(0, weight=5)
        input_frame.grid_rowconfigure(0, weight=1)

        send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_button.grid(row=0, column=1, sticky="nsew")
        input_frame.grid_columnconfigure(1, weight=1)

        clear_button = ttk.Button(input_frame, text="Clear", command=self.clear_conversation)
        clear_button.grid(row=0, column=2, sticky="nsew")
        input_frame.grid_columnconfigure(2, weight=1)

        reset_button = ttk.Button(input_frame, text="Reset", command=self.reset_conversation)
        reset_button.grid(row=0, column=3, sticky="nsew")
        reset_button.bind("<Enter>", self.show_tooltip)
        reset_button.bind("<Leave>", self.hide_tooltip)
        input_frame.grid_columnconfigure(3, weight=1)

        self.tooltip_label = ttk.Label(self.root, background="yellow")

    def fetch_reply(self):
        model = self.model_var.get()
        message = self.user_input.get("1.0", tk.END).strip()
        if not message:
            return
        self.messages.append({"role": "user", "content": message})
        self.progress_bar.start()
        try:
            if model == "text-davinci-003":
                
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=message,
                    temperature=float(self.temperature_var.get()),
                    max_tokens=int(self.max_tokens_var.get())
                )
                reply = response["choices"][0]["text"]
            else:
                
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=self.messages,
                    temperature=float(self.temperature_var.get()),
                    max_tokens=int(self.max_tokens_var.get())
                )
                reply = response["choices"][0]["message"]["content"]
        except openai.error.InvalidRequestError as e:
            reply = str(e)
        self.messages.append({"role": "assistant", "content": reply})
        self.update_conversation()
        self.user_input.delete("1.0", tk.END)
        self.progress_bar.stop()


    def send_message(self):
        threading.Thread(target=self.fetch_reply).start()

    def send_message_on_enter(self, event):
        self.send_message()

    def update_conversation(self):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.delete(1.0, tk.END)
        self.conversation.tag_config('red', foreground='red')
        for message in self.messages:
            role = message["role"].capitalize()
            content = message["content"]
            if role == 'Assistant':
                self.conversation.insert(tk.END, f"{role}: ", 'red')
                self.conversation.insert(tk.END, f"{content}\n\n")
            else:
                self.conversation.insert(tk.END, f"{role}: {content}\n\n")
        self.conversation.config(state=tk.DISABLED)
        self.conversation.yview(tk.END)

    def clear_conversation(self):
        self.messages.clear()
        self.update_conversation()

    def reset_conversation(self):
        self.messages.clear()
        self.messages.append({"role": "system", "content": self.context_entry.get("1.0", tk.END).strip()})
        self.update_conversation()

    def show_tooltip(self, event):
        self.tooltip_label.config(text="Reset the conversation and start with the initial system message.")
        self.tooltip_label.place(relx=event.x_root/self.root.winfo_screenwidth(), rely=event.y_root/self.root.winfo_screenheight())

    def hide_tooltip(self, event):
        self.tooltip_label.place_forget()

    def on_closing(self):
        self.config_manager.save_model(self.model_var.get())
        self.config_manager.save_temperature(self.temperature_var.get())
        self.config_manager.save_max_tokens(self.max_tokens_var.get())
        self.root.destroy()

    def api_key_entry_popup(self):
        hidden_root = tk.Tk()
        hidden_root.withdraw()
        api_key_entry_window = tk.Toplevel(hidden_root)
        api_key_entry_window.geometry("400x160")
        api_key_entry_window.title("API Key Entry")
        label = ttk.Label(api_key_entry_window, text="Enter your OpenAI API key:")
        label.pack(pady=10)
        warning_label = ttk.Label(api_key_entry_window, text="", foreground="red")
        warning_label.pack()
        api_key_var = tk.StringVar()
        api_key_entry = ttk.Entry(api_key_entry_window, textvariable=api_key_var, width=55)
        api_key_entry.pack(pady=5)

        def submit():
            if not api_key_var.get().strip():
                warning_label.config(text="API key cannot be blank!")
                return
            elif not self.config_manager.validate_api_key(api_key_var.get().strip()):
                warning_label.config(text="API key is invalid!")
                return
            self.config_manager.save_key(api_key_var.get())
            api_key_entry_window.destroy()
            hidden_root.destroy()

        def on_api_key_window_closing():
            api_key_entry_window.destroy()
            hidden_root.destroy()
            exit()

        api_key_entry_window.protocol("WM_DELETE_WINDOW", on_api_key_window_closing)
        submit_button = ttk.Button(api_key_entry_window, text="Submit", command=submit)
        submit_button.pack(pady=10)
        api_key_entry_window.mainloop()

    def setup_theme_menu(self):
        self.theme_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="Themes", menu=self.theme_menu)
        self.theme_var = tk.StringVar(value=self.current_theme)
        themes = self.root.get_themes()
        for theme in themes:
            self.theme_menu.add_radiobutton(label=theme, variable=self.theme_var, value=theme, command=self.change_theme)

    def change_theme(self):
        chosen_theme = self.theme_var.get()
        self.root.set_theme(chosen_theme)
        self.config_manager.save_theme(chosen_theme)

    def setup_settings_menu(self):
        models = [("gpt-3.5-turbo", "GPT-3.5 Turbo: Most advanced text-davinci model"),
                ("gpt-4", "GPT-4: Most advanced GPT model"),
                ("text-davinci-003", "Text-Davinci-003: Previous version of the text-davinci model")]

        gpt_3_5_turbo_menu = tk.Menu(self.settings_menu, tearoff=0)
        gpt_3_5_turbo_menu.add_radiobutton(label="GPT-3.5 Turbo", variable=self.model_var, value="gpt-3.5-turbo")
        gpt_3_5_turbo_menu.add_radiobutton(label="GPT-3.5 Turbo-16k: 4x the context length of standard GPT-3.5 Turbo", variable=self.model_var, value="gpt-3.5-turbo-16k")

        self.settings_menu.add_cascade(label="Model", menu=self.create_submenu(self.settings_menu, self.model_var, models, gpt_3_5_turbo_menu))

        temperatures = [("0.2", "0.2: More focused and deterministic responses"),
                        ("0.5", "0.5: Balanced between focused and random responses"),
                        ("0.8", "0.8: More random responses"),
                        ("1.0", "1.0: Completely random responses")]
        self.settings_menu.add_cascade(label="Temperature", menu=self.create_submenu(self.settings_menu, self.temperature_var, temperatures))

        max_tokens = [("50", "50 tokens: Short responses"),
                    ("100", "100 tokens: Medium length responses"),
                    ("150", "150 tokens: Slightly longer responses"),
                    ("200", "200 tokens: Long responses"),
                    ("300", "300 tokens: Very long responses"),
                    ("400", "400 tokens: Extremely long responses")]
        self.settings_menu.add_cascade(label="Max Tokens", menu=self.create_submenu(self.settings_menu, self.max_tokens_var, max_tokens))

    def create_submenu(self, parent_menu, variable, options, gpt_3_5_turbo_menu=None):
        created_menu = tk.Menu(parent_menu, tearoff=0)
        for option, description in options:
            if option == "gpt-4":
                gpt4_menu = tk.Menu(created_menu, tearoff=0)
                gpt4_menu.add_radiobutton(label="GPT-4", variable=variable, value="gpt-4")
                gpt4_menu.add_radiobutton(label="GPT-4-32k: 4x the context length of standard GPT-4", variable=variable, value="gpt-4-32k")
                created_menu.add_cascade(label=description, menu=gpt4_menu)
            elif option == "gpt-3.5-turbo":
                created_menu.add_cascade(label=description, menu=gpt_3_5_turbo_menu)
            else:
                created_menu.add_radiobutton(label=description, variable=variable, value=option)
        return created_menu

if __name__ == "__main__":
    ChatbotUI()
