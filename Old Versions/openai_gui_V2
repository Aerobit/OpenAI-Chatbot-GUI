import openai
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import scrolledtext
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from uuid import getnode as get_mac
from sys import exit

CONFIG_FILE = 'config.json'
base_key = 'GRO9jNw5lXc4U5B8_Wz3zAaPPhQDgWFQ8CQxnLhxjJ0='
mac = ':'.join(('%012X' % get_mac())[i:i+2] for i in range(0, 12, 2))
hashed_key = hashlib.sha256((mac + base_key).encode()).digest()
SECRET_KEY = base64.urlsafe_b64encode(hashed_key[:32])
cipher = Fernet(SECRET_KEY)


class APIKeyManager:
    def __init__(self):
        self.config_file = CONFIG_FILE

    def process_key(self, api_key):
        return cipher.encrypt(api_key.encode()).decode()

    def reverse_processing(self, processed_key):
        return cipher.decrypt(processed_key.encode()).decode()

    def retrieve_key(self):
        try:
            with open(self.config_file, 'r') as file:
                processed_key = file.readline().strip()
                return self.reverse_processing(processed_key)
        except FileNotFoundError:
            return None

    def save_key(self, api_key):
        processed_key = self.process_key(api_key)
        with open(self.config_file, 'w') as file:
            file.write(processed_key)

    def remove_key(self):
        try:
            os.remove(self.config_file)
        except FileNotFoundError:
            pass

    def validate_api_key(self, api_key):
        try:
            openai.api_key = api_key
            openai.Completion.create(model="text-davinci-003", prompt="Test", max_tokens=5)
            return True
        except openai.OpenAIError:
            return False


class ChatbotUI:
    def __init__(self):
        self.api_key_manager = APIKeyManager()

        self.api_key = self.api_key_manager.retrieve_key()
        if not self.api_key:
            self.api_key_entry_popup()
            self.api_key = self.api_key_manager.retrieve_key()

        if not self.api_key:  # If still None after the popup, just exit.
            exit()

        openai.api_key = self.api_key.strip()

        self.root = ThemedTk(theme="plastik")
        self.root.title("Chatbot")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        self.setup_ui()
        self.messages = [{"role": "system", "content": self.context_var.get()}]
        self.update_conversation()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def setup_ui(self):
        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.root.grid_columnconfigure(i, weight=1)

        self.model_var = tk.StringVar(value="gpt-3.5-turbo")
        self.temperature_var = tk.StringVar(value="0.8")
        self.max_tokens_var = tk.StringVar(value="300")
        self.context_var = tk.StringVar(value="You are a helpful assistant.")

        ttk.Label(self.root, text="Model:").grid(row=0, column=0)
        ttk.Entry(self.root, textvariable=self.model_var).grid(row=0, column=1)
        ttk.Label(self.root, text="Temperature:").grid(row=1, column=0)
        ttk.Entry(self.root, textvariable=self.temperature_var).grid(row=1, column=1)
        ttk.Label(self.root, text="Max Tokens:").grid(row=2, column=0)
        ttk.Entry(self.root, textvariable=self.max_tokens_var).grid(row=2, column=1)
        ttk.Label(self.root, text="Context:").grid(row=3, column=0)
        ttk.Entry(self.root, textvariable=self.context_var).grid(row=3, column=1)

        self.conversation = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)
        self.conversation.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.user_input = ttk.Entry(self.root, width=70)
        self.user_input.grid(row=5, column=0, padx=10, pady=10)
        self.user_input.bind("<Return>", self.send_message_on_enter)

        send_button = ttk.Button(self.root, text="Send", command=self.send_message)
        send_button.grid(row=5, column=1, padx=10, pady=10)

        reset_button = ttk.Button(self.root, text="Reset", command=self.reset_conversation)
        reset_button.grid(row=5, column=2, padx=10, pady=10)
        reset_button.bind("<Enter>", self.show_tooltip)
        reset_button.bind("<Leave>", self.hide_tooltip)

        self.tooltip_label = ttk.Label(self.root, background="yellow")

    def send_message(self):
        message = self.user_input.get()
        if not message.strip():
            return
        self.messages.append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            model=self.model_var.get(),
            messages=self.messages,
            temperature=float(self.temperature_var.get()),
            max_tokens=int(self.max_tokens_var.get())
        )
        reply = response["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})
        self.update_conversation()
        self.user_input.delete(0, tk.END)

    def send_message_on_enter(self, event):
        self.send_message()

    def update_conversation(self):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.delete(1.0, tk.END)
        for message in self.messages:
            role = message["role"].capitalize()
            content = message["content"]
            self.conversation.insert(tk.END, f"{role}: {content}\n\n")
        self.conversation.config(state=tk.DISABLED)
        self.conversation.yview(tk.END)

    def reset_conversation(self):
        self.messages.clear()
        self.messages.append({"role": "system", "content": self.context_var.get()})
        self.update_conversation()

    def show_tooltip(self, event):
        self.tooltip_label.config(text="Reset the conversation and start with the initial system message.")
        self.tooltip_label.place(relx=event.x_root/self.root.winfo_screenwidth(), rely=event.x_root/self.root.winfo_screenheight())

    def hide_tooltip(self, event):
        self.tooltip_label.place_forget()

    def on_closing(self):
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
            elif not self.api_key_manager.validate_api_key(api_key_var.get().strip()):
                warning_label.config(text="API key is invalid!")
                return
            self.api_key_manager.save_key(api_key_var.get())
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


if __name__ == "__main__":
    ChatbotUI()
