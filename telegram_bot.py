import os
import telebot
import requests
import json

API_URL = 'http://52.226.125.28/'
API_KEY = 'ragflow-ZlN2I2M2VhZTY5ZjExZWZiM2MwMDI0Mm'
chat_id = 'a926b1dee6b311ef93150242ac120006'  # Chat ID of the assistant
bot_token = '7251601028:AAEuIhoCCUPiYETtgC3CHQ9AiPvlvZ14lcQ'  # Your bot's token
bot = telebot.TeleBot(bot_token)

# Dictionary to store session IDs for users
user_sessions = {}

def create_chat_session_with_assistant(chat_id, name, user_id=None):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Prepare the data for the new chat session with the assistant
    data = {
        "name": name
    }

    if user_id:
        data["user_id"] = user_id  # Add user_id if provided

    try:
        # Send the POST request to create a new chat session with the assistant
        response = requests.post(f"{API_URL}/api/v1/chats/{chat_id}/sessions", json=data, headers=headers)

        if response.status_code == 200:  # Check for successful response
            result = response.json()
            if result["code"] == 0:
                print("Session created successfully.")
                return result['data']['id']
            else:
                print(f"Failed to create chat session: {result['message']}")
                return None
        else:
            print(f"Failed to create chat session: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

def converse_with_chat_assistant(session_id, question):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Prepare the data for conversing with the chat assistant
    data = {
        "question": question,
        "stream": False,
        "session_id": session_id
    }

    try:
        # Send the POST request to converse with the assistant
        response = requests.post(f"{API_URL}/api/v1/chats/{chat_id}/completions", json=data, headers=headers)

        if response.status_code == 200:  # Check for successful response
            result = response.json()
            if result["code"] == 0:
                return result['data']['answer']
            else:
                print(f"Failed to converse with assistant: {result['message']}")
                return None
        else:
            print(f"Failed to initiate conversation: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    print("receive hello")
    bot.reply_to(message, "Hello! Type /new_chat to start a new conversation with the assistant.")

@bot.message_handler(commands=['new_chat'])
def start_new_chat(message):
    user_id = message.from_user.id  # Get the unique user ID
    session_id = create_chat_session_with_assistant(chat_id, f"User_{user_id}_Chat")

    if session_id:
        user_sessions[user_id] = session_id  # Store the session ID
        bot.reply_to(message, "New chat session created! You can now ask questions.")
    else:
        bot.reply_to(message, "Failed to create a new chat session. Try again later.")

@bot.message_handler(func=lambda message: message.text and message.text != '/new_chat')
def handle_question(message):
    user_id = message.from_user.id  # Get the unique user ID
    if user_id in user_sessions:
        session_id = user_sessions[user_id]
        question = message.text
        answer = converse_with_chat_assistant(session_id, question)

        if answer:
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, "Sorry, I couldn't get an answer.")
    else:
        bot.reply_to(message, "Please start a new chat first by typing /new_chat.")

# id = create_chat_session_with_assistant(chat_id, f"okeem")
# print(id)
print("Bot is polling...")  # This should print once the bot starts polling
try:
    bot.infinity_polling()
except Exception as e:
    print(f"Error occurred during polling: {e}")

print("Bot stopped polling...")
