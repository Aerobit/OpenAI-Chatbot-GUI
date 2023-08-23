# OpenAI Chatbot GUI

A user-friendly interface for interacting with OpenAI's GPT-3 model.

## 🌟 Features

- **Interactive GUI**: Engage in fluent conversations with AI through a clean, intuitive interface.
- **Dynamic Configurations**: Modify model parameters including temperature, max tokens, and context on-the-fly.
- **Secure API Key Management**: Uses `cryptography` for safe storage and retrieval of your OpenAI API key. The key is encrypted in conjunction with your computer's MAC address for extra security.
- **Scrollable Conversation Area**: View and scroll through your past interactions.
- **Error Handling**: Gracefully handles invalid API keys and other potential issues.

## 🛠 Prerequisites

- Python 3
- Required Python packages:
  - `openai`
  - `tkinter`
  - `ttkthemes`
  - `cryptography`
  - `hashlib`
  - `base64`

## 🚀 Getting Started

1. **Clone the Repository**
   ```shell
   git clone https://github.com/Aerobit/OpenAI-Chatbot-GUI.git
   ```

2. **Install Dependencies**
   Navigate to the project directory and install the required packages:
   ```shell
   pip install openai ttkthemes cryptography hashlib base64
   ```

3. **Run the Application**
   Execute the `OpenAI_GUI.py` script. If it's your first run, you'll be prompted to enter your OpenAI API key.

4. **Engage with AI**
   Type your queries and enjoy conversing with the chatbot.

## ⚙ Configuration

- The API key is fetched from a `config.json` file in the project's root.
- Your key undergoes encryption using a combination of a predefined key and your machine's MAC address, ensuring security.
- If the key is invalid or absent, you'll be prompted for re-entry.

## 📖 Usage

1. **Message Input**: Type in your query in the provided text box.
2. **Send & Receive**: Click "Send" or press "Enter" to get a response from the AI.
3. **Adjust Settings**: Tweak model parameters as needed for a personalized experience.
4. **Reset Session**: Use "Reset" to clear the chat history and start anew.

## 📜 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute as you see fit.  
[MIT License](https://choosealicense.com/licenses/mit/)
