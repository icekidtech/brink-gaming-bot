import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from bot.config import DATABASE_URL

# Loading environment variables from .env file
load_dotenv()

# Accessing environment variables
DATABASE_URL = os.getenv('DATABASE_URL')

# Function to establish a connection to the database
def get_db_connection():
    try:
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
# Function to initialize the database (create tables if they don't exist)
def initialize_db():
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        telegram_username TEXT NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        passcode TEXT NOT NULL,
                        country TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                )
                connection.commit()
                print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            connection.close()
                       
initialize_db()           
            
def add_user(email, hashed_passcode, telegram_username, country):
    query = """
    INSERT INTO users (email, passcode, telegram_username, country)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (email) DO NOTHING;
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(query, (email, hashed_passcode, telegram_username, country))
        conn.commit()
    except Exception as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()

# Function to fecth users        
def fetch_user_by_email(email):
    try:
        connection = get_db_connection()
        if connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:  # Use RealDictCursor
                query = "SELECT * FROM users WHERE email = %s"
                cursor.execute(query, (email,))
                user_data = cursor.fetchone()
                if user_data:
                    # Map database fields to the dictionary
                    user = {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "passcode": user_data["passcode"],
                        "telegram_username": user_data["telegram_username"],
                        "country": user_data["country"],
                        "created_at": user_data["created_at"],
                        "title": user_data.get("title", "New User"),  # Default value if title is NULL
                        "leaderboard_position": user_data.get("leaderboard_position", "000th"),  # Default value if NULL
                        "total_submissions": user_data.get("total_submissions", 0),  # Default value if NULL
                    }
                    return user
                else:
                    return None  # No user found
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        if connection:
            connection.close()
    print(f"Query result: {user_data}")