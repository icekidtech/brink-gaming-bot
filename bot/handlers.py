from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from .database import get_db_connection
from bot import bot # Ensure bot instance is imported

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

@bot.message_handler(func=lambda msg: msg.text == "Login")
def login(message):
    bot.send_message(message.chat.id, "Please enter your email:")
    bot.register_next_step_handler(message, verify_login)
    
def verify_login(message):
    email = message.text
    # Query the database to check if the email exists
    from bot.database import fetch_user_by_email
    user = fetch_user_by_email(email)
    
    if user:
        bot.send_message(message.chat.id, "Enter your passcode:")
        bot.register_next_step_handler(message, verify_passcode, email)
    else:
        bot.send_message(message.chat.id, "Email not found. Please register first.")
        
def verify_passcode(message, email):
    passcode = message.text
    # Query the database to check if the passcode matches
    from bot.database import fetch_user_by_email
    user = fetch_user_by_email(email)
    
    if user and user['passcode'] == passcode:
        # Successful login
        bot.send_message(message.chat.id, "Login successful! Redirecting to your dashboard...")
        show_dashboard(message, user)
    else:
        bot.send_message(message.chat.id, "Incorrect passcode. Please try again.")
        
def show_dashboard(message, user):
    # Assuming `user` is a dictionary with user's info
    username = message.from_user.username or "User"
    dashboard_text = f"""
    Welcome back, {username}! 🎉
    Your current status:

    🎖️ Title: {user.get('title', 'New User')}
    ♟️ Leaderboard Position: {user.get('leaderboard_position', '000th')}
    #⃣ Total Post Submissions: {user.get('total_submissions', 0)}
    🗺️ Region of Activity: {user.get('country', 'Unknown')}

    What would you like to do next?
    """
    # Create options for the dashboard
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Join Pool"), KeyboardButton("Submit Activity Login"))
    bot.send_message(message.chat.id, dashboard_text, reply_markup=markup) 
        
# Debug messages to check what the bot is receiving
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f"Received message: {message.text}")
    bot.reply_to(message, "I see your message!")