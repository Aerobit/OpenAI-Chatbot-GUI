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

CONFIG_FILE = 'config.json'

base_key = 'GRO9jNw5lXc4U5B8_Wz3zAaPPhQDgWFQ8CQxnLhxjJ0='
mac = ':'.join(('%012X' % get_mac())[i:i+2] for i in range(0, 12, 2))
hashed_key = hashlib.sha256((mac + base_key).encode()).digest()
SECRET_KEY = base64.urlsafe_b64encode(hashed_key[:32])
cipher = Fernet(SECRET_KEY)

def process_key(api_key):
    return cipher.encrypt(api_key.encode()).decode()

def reverse_processing(processed_key):
    return cipher.decrypt(processed_key.encode()).decode()

def retrieve_key():
    try:
        with open(CONFIG_FILE, 'r') as file:
            processed_key = file.readline().strip()
            return reverse_processing(processed_key)
    except FileNotFoundError:
        return None

def save_key(api_key):
    processed_key = process_key(api_key)
    with open(CONFIG_FILE, 'w') as file:
        file.write(processed_key)

def remove_key():
    try:
        os.remove(CONFIG_FILE)
    except FileNotFoundError:
        pass

def validate_api_key(api_key):
    try:
        openai.api_key = api_key
        openai.Completion.create(model="text-davinci-003", prompt="Test", max_tokens=5)
        return True
    except openai.OpenAIError:
        return False

def api_key_entry_popup():
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
        elif not validate_api_key(api_key_var.get().strip()):
            warning_label.config(text="API key is invalid!")
            return
        save_key(api_key_var.get())
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

def send_message():
    message = user_input.get()
    if not message.strip():
        return
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model=model_var.get(),
        messages=messages,
        temperature=float(temperature_var.get()),
        max_tokens=int(max_tokens_var.get())
    )
    reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    update_conversation()
    user_input.delete(0, tk.END)

def send_message_on_enter(event):
    send_message()

def update_conversation():
    conversation.config(state=tk.NORMAL)
    conversation.delete(1.0, tk.END)
    for message in messages:
        role = message["role"].capitalize()
        content = message["content"]
        conversation.insert(tk.END, f"{role}: {content}\n\n")
    conversation.config(state=tk.DISABLED)
    conversation.yview(tk.END)

def reset_conversation():
    messages.clear()
    messages.append({"role": "system", "content": context_var.get()})
    update_conversation()

def show_tooltip(event):
    global root
    tooltip_label.config(text="Reset the conversation and start with the initial system message.")
    tooltip_label.place(relx=event.x_root/root.winfo_screenwidth(), rely=event.x_root/root.winfo_screenheight())

def hide_tooltip(event):
    global root
    tooltip_label.place_forget()

def on_closing():
    global root
    root.destroy()

def main():
    global user_input, conversation, messages, model_var, temperature_var, max_tokens_var, context_var, tooltip_label, root
    api_key = retrieve_key()

    if not api_key:
        api_key_entry_popup()
        api_key = retrieve_key()

    openai.api_key = api_key.strip()

    root = ThemedTk(theme="plastik")
    root.title("Chatbot")
    root.geometry("700x500")
    root.resizable(True, True)

    for i in range(6):
        root.grid_rowconfigure(i, weight=1)
    for i in range(3):
        root.grid_columnconfigure(i, weight=1)

    model_var = tk.StringVar(value="gpt-3.5-turbo")
    temperature_var = tk.StringVar(value="0.8")
    max_tokens_var = tk.StringVar(value="300")
    context_var = tk.StringVar(value="You are a helpful assistant.")

    ttk.Label(root, text="Model:").grid(row=0, column=0)
    ttk.Entry(root, textvariable=model_var).grid(row=0, column=1)
    ttk.Label(root, text="Temperature:").grid(row=1, column=0)
    ttk.Entry(root, textvariable=temperature_var).grid(row=1, column=1)
    ttk.Label(root, text="Max Tokens:").grid(row=2, column=0)
    ttk.Entry(root, textvariable=max_tokens_var).grid(row=2, column=1)
    ttk.Label(root, text="Context:").grid(row=3, column=0)
    ttk.Entry(root, textvariable=context_var).grid(row=3, column=1)

    conversation = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)
    conversation.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    user_input = ttk.Entry(root, width=70)
    user_input.grid(row=5, column=0, padx=10, pady=10)
    user_input.bind("<Return>", send_message_on_enter)

    send_button = ttk.Button(root, text="Send", command=send_message)
    send_button.grid(row=5, column=1, padx=10, pady=10)

    reset_button = ttk.Button(root, text="Reset", command=reset_conversation)
    reset_button.grid(row=5, column=2, padx=10, pady=10)
    reset_button.bind("<Enter>", show_tooltip)
    reset_button.bind("<Leave>", hide_tooltip)

    tooltip_label = ttk.Label(root, background="yellow")

    messages = [{"role": "system", "content": context_var.get()}]
    update_conversation()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
