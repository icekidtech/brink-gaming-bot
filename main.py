# main.py
from bot import bot
from bot.handlers import * 

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling()