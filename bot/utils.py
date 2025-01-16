import re

# Utility function to validate email format
def validate_email(email):
    """
    Validates the format of the email address.
    :param email: Email address to validate.
    :return: True if valid, False otherwise.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Utility function to generate a referral link
def generate_referral_link(username, bot_username):
    """
    Generates a unique referral link for a user.
    :param username: Telegram username of the user.
    :param bot_username: Telegram bot username.
    :return: Referral link as a string.
    """
    return f"https://t.me/{bot_username}?start={username}"

# Utility function to validate country input
def validate_country(country):
    """
    Validates that the country input is a string and not empty.
    :param country: Country name to validate.
    :return: True if valid, False otherwise.
    """
    return bool(country.strip()) and country.isalpha()