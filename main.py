# main.py
from bot import bot
from bot.handlers import welcome

if __name__ == '__main__':
    welcome(bot)
    print("Bot is running...")
    bot.polling()