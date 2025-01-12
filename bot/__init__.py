# bot/__init__.py
import os
from telebot import TeleBot
from .config import Bot_API_TOKEN
from dotenv import load_dotenv

load_dotenv()

# Retrieve variables
Bot_API_TOKEN = os.getenv("Bot_API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

bot = TeleBot(Bot_API_TOKEN)