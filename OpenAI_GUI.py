import openai
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import scrolledtext
import os
from cryptography.fernet import Fernet

CONFIG_FILE = 'config.txt'

# Split the key into parts and reassemble it at runtime
part_1 = 'GRO9jNw5lXc4U5B8_'
part_2 = 'Wz3zAaPPhQDgWFQ8'
part_3 = 'CQxnLhxjJ0='
SECRET_KEY = (part_1 + part_2 + part_3).encode()

# Create a Fernet cipher using the hardcoded key
cipher = Fernet(SECRET_KEY)

# Process the API key
def process_key(api_key):
    return cipher.encrypt(api_key.encode()).decode()

# Reverse the processing
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

def update_conversation():
    conversation.config(state=tk.NORMAL)
    conversation.delete(1.0, tk.END)
    for message in messages:
        role = message["role"].capitalize()
        content = message["content"]
        conversation.insert(tk.END, f"{role}: {content}\n")
    conversation.config(state=tk.DISABLED)
    conversation.yview(tk.END)

def reset_conversation():
    messages.clear()
    messages.append({"role": "system", "content": context_var.get()})
    update_conversation()

def show_tooltip(event):
    global root
    tooltip_label.config(text="Reset the conversation and start with the initial system message.")
    tooltip_label.place(relx=event.x_root/root.winfo_screenwidth(), rely=event.y_root/root.winfo_screenheight())

def hide_tooltip(event):
    global root
    tooltip_label.place_forget()

def main():
    global user_input, conversation, messages, model_var, temperature_var, max_tokens_var, context_var, tooltip_label, root
    api_key = retrieve_key()
    if not api_key:
        print("No API key found. Please enter your OpenAI API key.")
        api_key = input("Enter your OpenAI API key: ")
        save_key(api_key)
    openai.api_key = api_key
    print("API key set.")

    root = ThemedTk(theme="arc")
    root.title("Chatbot")
    root.geometry("700x500")

    ttk.Label(root, text="Model:").grid(row=0, column=0)
    model_var = tk.StringVar(value="gpt-3.5-turbo")
    ttk.Entry(root, textvariable=model_var).grid(row=0, column=1)

    ttk.Label(root, text="Temperature:").grid(row=1, column=0)
    temperature_var = tk.StringVar(value="0.7")
    ttk.Entry(root, textvariable=temperature_var).grid(row=1, column=1)

    ttk.Label(root, text="Max Tokens:").grid(row=2, column=0)
    max_tokens_var = tk.StringVar(value="150")
    ttk.Entry(root, textvariable=max_tokens_var).grid(row=2, column=1)

    ttk.Label(root, text="Context:").grid(row=3, column=0)
    context_var = tk.StringVar(value="You are a helpful assistant.")
    ttk.Entry(root, textvariable=context_var).grid(row=3, column=1)

    conversation = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, state=tk.DISABLED)
    conversation.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

    user_input = ttk.Entry(root, width=70)
    user_input.grid(row=5, column=0, padx=10, pady=10)

    send_button = ttk.Button(root, text="Send", command=send_message)
    send_button.grid(row=5, column=1, padx=10, pady=10)

    reset_button = ttk.Button(root, text="Reset", command=reset_conversation)
    reset_button.grid(row=5, column=2, padx=10, pady=10)
    reset_button.bind("<Enter>", show_tooltip)
    reset_button.bind("<Leave>", hide_tooltip)

    tooltip_label = ttk.Label(root, background="yellow")
    
    messages = [{"role": "system", "content": context_var.get()}]
    update_conversation()
    root.mainloop()

if __name__ == "__main__":
    main()



