from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from .database import get_db_connection

# Import bot instance from __init__.py
from . import bot

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = "Welcome to our bot! 🎉 Please select an option:"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Sign Up"), KeyboardButton("Join Community"), KeyboardButton("Login"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Sign Up")
def sign_up(message):
    bot.send_message(message.chat.id, "Please provide your email:")
    bot.register_next_step_handler(message, collect_email)

def collect_email(message):
    email = message.text
    if not validate_email(email):
        bot.send_message(message.chat.id, "Invalid email format. Please start again.")
        return
    bot.send_message(message.chat.id, "Set a secure passcode:")
    bot.register_next_step_handler(message, set_passcode, email)

def set_passcode(message, email):
    passcode = message.text
    bot.send_message(message.chat.id, "Confirm your passcode:")
    bot.register_next_step_handler(message, confirm_passcode, email, passcode)

def confirm_passcode(message, email, passcode):
    confirm = message.text
    if confirm == passcode:
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (telegram_username, email, passcode, country)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (message.chat.username, email, passcode, "Not provided")
                )
                connection.commit()
                bot.send_message(message.chat.id, "Account created successfully! 🎉")
        except Exception as e:
            bot.send_message(message.chat.id, f"Error saving to database: {e}")
        finally:
            if connection:
                connection.close()
    else:
        bot.send_message(message.chat.id, "Passcodes do not match. Please start again.")

def validate_email(email):
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None
