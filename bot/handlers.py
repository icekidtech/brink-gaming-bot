from email import message
import email
import os
from datetime import datetime
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from bot.database import add_user, fetch_user_by_email, fetch_user_by_username, update_user_referrals, get_total_users, update_user_tasks

# Initialize bot with token
API_TOKEN = os.getenv("Bot_API_TOKEN")
bot = TeleBot(API_TOKEN)

# Link to Telegram community
COMMUNITY_LINK = "https://t.me/your_community_link"  # Replace with your community link

# Start the bot and handle commands
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username
    welcome_text = f"Welcome, @{username or 'User '}! 🎉\nChoose an option to continue:"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Sign Up"), 
        KeyboardButton("Join Community"), 
        KeyboardButton("Login")
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

    # Handle referral logic
    if len(message.text.split()) > 1:
        referrer_username = message.text.split()[1]
        referrer = fetch_user_by_username(referrer_username)
        if referrer:
            update_user_referrals(referrer_username)
            bot.send_message(message.chat.id, f"You were referred by @{referrer_username}. Thank you for joining!")

    # Handle the "Sign Up" process
    @bot.message_handler(func=lambda msg: msg.text == "Sign Up")
    def sign_up(message):
        username = message.from_user.username
        existing_user = fetch_user_by_username(username)
        if existing_user:
            bot.send_message(message.chat.id, "You already have an account. Please log in.")
            return
        bot.send_message(message.chat.id, "Please provide your email:")
        bot.register_next_step_handler(message, collect_email)

    # Collect email during sign-up
    def collect_email(message):
        email = message.text
        existing_user = fetch_user_by_email(email)
        if existing_user:
            bot.send_message(message.chat.id, "This email is already registered. Please use a different email.")
            return
        bot.send_message(message.chat.id, "Enter your country:")
        bot.register_next_step_handler(message, set_country, email)

    # Set country during sign-up
    def set_country(message, email):
        country = message.text
        username = message.from_user.username
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        referral_link = f"https://t.me/{bot.get_me().username}?start={username}"
        add_user(email, username, country, referral_link, join_date)  # Corrected parameter order
        bot.send_message(message.chat.id, "Account created successfully! ")
        show_dashboard(message, username)

    # Handle the "Login" process
    @bot.message_handler(func=lambda msg: msg.text == "Login")
    def login(message):
        username = message.from_user.username
        user = fetch_user_by_username(username)
        if user:
            bot.send_message(message.chat.id, "Login successful! Redirecting to your dashboard...")
            show_dashboard(message, username)
        else:
            bot.send_message(message.chat.id, "No account found. Please sign up first.")

    # Handle the "Join Community" option
    @bot.message_handler(func=lambda msg: msg.text == "Join Community")
    def join_community(message):
        bot.send_message(message.chat.id, "Redirecting you to the community...")
        bot.send_message(message.chat.id, COMMUNITY_LINK)

    # Display the user dashboard
    def show_dashboard(message, username):
        user = fetch_user_by_username(username)
        if user:
            total_users = get_total_users()
            total_tasks = user.get('total_tasks', 0)
            referrals = user.get('referrals', 0)
            join_date = user['created_at']
            dashboard_text = (
                f"Welcome back, @{username}! 🎖️\n\n"
                f"📊 Current Status:\n"
                f"📧 Email: {user['email']}\n"
                f"🗺️ Country: {user['country']}\n"
                f"#⃣ Number of completed tasks: {total_tasks}\n"
                f"🔗 Number of referrals: {referrals}\n"
                f"📅 Joined on: {join_date}\n"
                f"👥 Total users on bot: {total_users}\n\n"
                f"Share your referral link to invite others: {user['referral_link']}\n"
            )
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(
                KeyboardButton("Submit Task"), 
                KeyboardButton("View Referral Stats")
            )
            bot.send_message(message.chat.id, dashboard_text, reply_markup=markup)

    # Handle task submission
    @bot.message_handler(func=lambda msg: msg.text == "Submit Task")
    def submit_task(message):
        bot.send_message(message.chat.id, "Submit your task details:")
        bot.register_next_step_handler(message, record_task)

    # Record task completion
    def record_task(message):
        username = message.from_user.username
        user = fetch_user_by_username(username)
        if user:
            # Simulate task completion logic
            update_user_tasks(username)
            bot.send_message(message.chat.id, "Task submitted successfully!")
            
            # Adds a button to redisplay the dashboard
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(
                KeyboardButton("View dashboard")
            )
            bot.send_message(message.chat.id, "Click 'View dashboard' to see your updated stats", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "No account found. Please sign up first.")
            
# Handle the 'View dashboard' button click
@bot.message_handler(func=lambda msg: msg.text == "View dashboard")
def view_dashboard(message):
    username = message.from_user.username
    user = fetch_user_by_username(username)
    if user:
        total_users = get_total_users()
        total_tasks = user.get('total_tasks', 0)
        referrals = user.get('referrals', 0)
        join_date = user['created_at']
        dashboard_text = (
            f"Welcome back, @{username}! 🎖️\n\n"
            f"📊 Current Status:\n"
            f"📧 Email: {user['email']}\n"
            f"🗺️ Country: {user['country']}\n"
            f"#⃣ Number of completed tasks: {total_tasks}\n"
            f"🔗 Number of referrals: {referrals}\n"
            f"📅 Joined on: {join_date}\n"
            f"👥 Total users on bot: {total_users}\n\n"
            f"Share your referral link to invite others: {user['referral_link']}\n"
            )
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            KeyboardButton("Summit Task"),
            KeyboardButton("View Refferal Stats")
            )
        bot.send_message(message.chat.id, dashboard_text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "No account found. Please sign up first.")