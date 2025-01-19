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
                        email VARCHAR(255) NOT NULL,
                        country TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        total_tasks INT NOT NULL DEFAULT 0,
                        referrals INT NOT NULL DEFAULT 0,
                        referral_link TEXT NOT NULL DEFAULT ''
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

# Function to add a new user
def add_user(email, telegram_username, country, referral_link, join_date):
    query = """
    INSERT INTO users (email, telegram_username, country, referral_link, created_at)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (email, telegram_username) DO NOTHING;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (email, telegram_username, country, referral_link, join_date))
        connection.commit()
    except Exception as e:
        print(f"Error adding user: {e}")
    finally:
        if connection:
            connection.close()

# Function to fetch a user by email
def fetch_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by email: {e}")
        return None
    finally:
        if connection:
            connection.close()

# Function to fetch a user by username
def fetch_user_by_username(username):
    query = "SELECT * FROM users WHERE telegram_username = %s;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user by username: {e}")
        return None
    finally:
        if connection:
            connection.close()

# Function to update the total tasks completed by a user
def update_user_tasks(username):
    query = """
    UPDATE users
    SET total_tasks = total_tasks + 1
    WHERE telegram_username = %s
    RETURNING total_tasks;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            connection.commit()
            return result['total_tasks'] if result else None
    except Exception as e:
        print(f"Error updating tasks for {username}: {e}")
        return None
    finally:
        if connection:
            connection.close()

# Function to update referrals for a user
def update_user_referrals(referrer_username):
    query = """
    UPDATE users
    SET referrals = referrals + 1
    WHERE telegram_username = %s
    RETURNING referrals;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query, (referrer_username,))
            result = cursor.fetchone()
            connection.commit()
            return result['referrals'] if result else None
    except Exception as e:
        print(f"Error updating referrals for {referrer_username}: {e}")
        return None
    finally:
        if connection:
            connection.close()

# Function to get the total number of users
def get_total_users():
    query = "SELECT COUNT(*) AS total_users FROM users;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result['total_users'] if result else 0
    except Exception as e:
        print(f"Error fetching total users: {e}")
        return 0
    finally:
        if connection:
            connection.close()

# Function to clear users from the database            
def clear_users():
    query = "DELETE FROM users;"
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()
        print("Users cleared successfully.")
    except Exception as e:
        print(f"Error clearing users: {e}")
    finally:
        if connection:
            connection.close()