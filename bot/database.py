import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

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