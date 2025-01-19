# main.py
from bot import bot
from bot.handlers import * 
from bot.database import clear_users

if __name__ == '__main__':
    print("Bot is running...")
    #clear_users()
    bot.infinity_polling(timeout=60, long_polling_timeout=60)