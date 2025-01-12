import re
import hashlib

# Utility function to validate email format
def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

# Utility function to hash a passcode securely
def hash_passcode(passcode):
    return hashlib.sha256(passcode.encode()).hexdigest()

# Utility function to compare a plain-text passcode with a hashed passcode
def verify_passcode(plain_passcode, hashed_passcode):
    return hash_passcode(plain_passcode) == hashed_passcode

# Utility function to validate passcode length and strength
def validate_passcode(passcode):
    if len(passcode) < 6:
        return False, "Passcode must be at least 6 characters long."
    if not any(char.isdigit() for char in passcode):
        return False, "Passcode must contain at least one digit."
    if not any(char.isalpha() for char in passcode):
        return False, "Passcode must contain at least one letter."
    return True, "Passcode is valid."
