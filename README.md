# OpenAI-Chatbot-GUI

This project provides a simple graphical interface for interacting with OpenAI's GPT-3 model using the `openai` Python package. The user can send messages to the chatbot and receive responses, with the conversation displayed in a scrollable text area.

## Features

- **Interactive Chat:** Engage in real-time conversation with the chatbot.
- **Customizable Parameters:** Adjust the model, temperature, max tokens, and context directly from the GUI.
- **Secure API Key Storage:** Your OpenAI API key is encrypted and stored securely. It's combined with the MAC address of your computer to create an additional layer of security.
- **Resizable GUI:** The chatbot window can be resized as per the user's preference.
- **Reset Conversation:** Easily reset the conversation to start afresh.
- **Keyboard Shortcut:** Send messages by pressing the "Enter" key.

## Prerequisites

- Python 3
- `openai` Python package
- `tkinter`
- `ttkthemes`
- `cryptography`
- `hashlib`
- `base64`

## Getting Started

1. Clone this repository.
2. Install the required Python packages.
   ```shell
   pip install openai tkinter ttkthemes cryptography hashlib base64
3. Run the OpenAI_GUI.py script.
4. If it's your first time running the script, you'll be prompted to enter your OpenAI API key.
   Once the GUI appears, you can start chatting with the bot.

## Configuration

-  The chatbot retrieves the OpenAI API key from a configuration file (config.json) saved in the working directory.
-  The key is encrypted using a combination of a static key and the MAC address of the computer to enhance security. 
-  If the configuration file is missing or the key is not valid, you'll be prompted to enter it again.

## Usage

-  Type your message in the text box.
-  Click the "Send" button or press "Enter" to send the message.
-  View the chatbot's response in the conversation area.
-  Adjust the model, temperature, max tokens, or context as desired.
-  Click the "Reset" button to start a new conversation.

## License

-  This project is open-source and available under the MIT License.
