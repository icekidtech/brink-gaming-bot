from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from .database import get_db_connection
from bot import bot # Ensure bot instance is imported
from datetime import datetime
from bot.database import add_user, fetch_user_by_email, fetch_user_by_username, update_user_posts, update_leaderboard


# Import bot instance from __init__.py
from . import bot

# Function to initialize the bot
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = "Welcome to our Brink bot! 🎉 Please select an option:"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Sign Up"), KeyboardButton("Join Community"), KeyboardButton("Login"))
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# Fuction to handle sign up
@bot.message_handler(func=lambda msg: msg.text == "Sign Up")
def sign_up(message):
    username = message.from_user.username
    existing_user = fetch_user_by_username(username)
    if existing_user:
        bot.send_message(message.chat.id, "You already have an account. Please login instead.")
        return
    bot.send_message(message.chat,id, "Please enter your email address:")
    bot.register_next_step_handler(message, collect_email)
    
# Function to collect email
def collect_email(message):
    email = message.text
    existing_user = fetch_user_by_email(email)
    if existing_user:
            bot.send_message(message.chat.id, "This email is already registered. Please log.")
            return
    bot.send_message(message.chat.id, "Set a secure passcode:")
    bot.register_next_step_handler(message, set_passcode, email)

# Function to collect passcode
def set_passcode(message, email):
    passcode = message.text
    # Delete the user's passcode message for security
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Confirm your passcode:")
    bot.register_next_step_handler(message, confirm_passcode, email, passcode)

# Function to confirm passcode
def confirm_passcode(message, email, passcode):
    confirm = message.text
    # Delete the user's entry for security
    bot.delete_message(message.chat.id, message.message_id)
    if confirm == passcode:
            username = message.from_user.username
            join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            region = message.from_user.language_code
            add_user(username, email, passcode, join_date)
            bot.send_message(message.chat.id, "Account created successfully! 🎉")
            show_dashboard(message, username, email, join_date, region)
    else:
        bot.send_message(message.chat.id, "Passcodes do not match. Please start again by selecting 'Sign Up'.")

# Function to validate email address
def validate_email(email):
    import re
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Function to handle login logic
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
        email = message.text
        user = fetch_user_by_email(email)
        if not user:
            bot.send_message(message.chat.id, "No account found with this email. Please sign up first.")
            return
        bot.send_message(message.chat.id, "Enter your passcode:")
        bot.register_next_step_handler(message, verify_passcode, email)

# Function to verify passcode        
def verify_passcode(message, email):
    passcode = message.text
    # Delete the user's passcode message for security
    bot.delete_message(message.chat.id, message.message_id)
    # Query the database to check if the passcode matches
    user = fetch_user_by_email(email)
    if user and user['passcode'] == passcode:
        bot.send_message(message.chat.id, "Login successful! Redirecting to your dashboard...")
        show_dashboard(message, user['username'], user['email'], user['join_date', user['region']])
    else:
        bot.send_message(message.chat.id, "Incorrect passcode. Please try again.")
        
# Function to join community
@bot.message_handler(func=lambda msg: msg.text == "Join Community")
def join_community(message):
    community_link = "https://t.me/your_community_link"  # Replace with your community link
    bot.send_message(message.chat.id, f"Join our community here: {community_link}")
    
# Function to summit activity
@bot.message_handler(func=lambda msg: msg.text == "Submit Activity Login")
def submit_activity(message):
    bot.send_message(message.chat.id, "Submit your post link for verification:")
    bot.register_next_step_handler(message, record_activity)

def record_activity(message):
    post_link = message.text
    username = message.from_user.username
    if not username:
        bot.send_message(message.chat.id, "An error occurred. Please ensure your Telegram username is set.")
        return
    update_user_posts(username)
    update_leaderboard(username)
    bot.send_message(message.chat.id, "Your activity has been recorded. Thank you!")


# Function to show dashboard        
def show_dashboard(message, username, email, join_date, region):
    user = fetch_user_by_username
    if user:
        total_posts = user.get('total_posts', 0)
        leaderboard_position = user.get('leaderboard_position', '000th')
        dashboard_text = (
            f"Welcome back, @{username}! 🎖️\n\n"
            f"📊 Current Status:\n"
            f"♟️ Leaderboard position: {leaderboard_position}\n"
            f"#⃣ Total post submissions: {total_posts}\n"
            f"🗺️ Region of activity: {region or 'Unknown'}\n"
            f"📅 Joined on: {join_date}\n\n"
            f"Partake in the Contributors Pool and elevate your title on the platform! 👾"
        )
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
        KeyboardButton("Join Pool"), 
        KeyboardButton("Submit Activity Login")
        )
        bot.send_message(message.chat.id, dashboard_text, reply_markup=markup)
        
        
# Function to show leaderboard
@bot.message_handler(func=lambda msg: msg.text == "View Leaderboard")
def view_leaderboard(message):
    leaderboard = update_leaderboard()
    if leaderboard:
        leaderboard_text = "🏆 Leaderboard 🏆\n\n"
        for rank, (username, total_posts) in enumerate(leaderboard, start=1):
            leaderboard_text += f"{rank}. @{username} - {total_posts} posts\n"
        bot.send_message(message.chat.id, leaderboard_text)
    else:
        bot.send_message(message.chat.id, "Leaderboard is empty or unavailable.")

        
# Debug messages to check what the bot is receiving
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f"Received message: {message.text}")
    bot.reply_to(message, "I see your message!")