from dotenv import load_dotenv 
import os

# Load environment variables from .env file
load_dotenv()

# Debug: Print the current working directory
print(f"Current working directory: {os.getcwd()}")

# Access environment variables
Bot_API_TOKEN = os.getenv('Bot_API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Debug: Print the token to verify it's loaded
print(f"Bot_API_TOKEN: {Bot_API_TOKEN}")
print(f"DATABASE_URL: {DATABASE_URL}")