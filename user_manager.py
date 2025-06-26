import json
import os
import datetime

# ##############################################################################
# MODULE 4 & 6: USER & CREDENTIAL MANAGEMENT
#
# This script manages user data, including Beehive credentials and leave dates.
# ##############################################################################

USER_FILE = 'users.json'

def load_users():
    """Loads user data from the JSON file."""
    if not os.path.exists(USER_FILE):
        save_users({})
        return {}
    try:
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_users(users_data):
    """Saves the user data dictionary to the JSON file."""
    try:
        with open(USER_FILE, 'w') as f:
            json.dump(users_data, f, indent=4)
        return True
    except IOError:
        return False

def add_user(telegram_id, beehive_username, beehive_password):
    """Adds a new user or updates an existing user's details."""
    users = load_users()
    str_telegram_id = str(telegram_id)
    users[str_telegram_id] = {
        "beehive_username": beehive_username,
        "beehive_password": beehive_password,
        # *** CHANGE: Added leave_dates list for new users. ***
        "leave_dates": []
    }
    return save_users(users)

# *** NEW: Function to add a leave date for a user. ***
def add_leave_date(telegram_id, leave_date_str):
    """Adds a leave date (YYYY-MM-DD) for a specific user."""
    users = load_users()
    str_telegram_id = str(telegram_id)
    if str_telegram_id in users:
        # Avoid duplicate dates
        if leave_date_str not in users[str_telegram_id]['leave_dates']:
            users[str_telegram_id]['leave_dates'].append(leave_date_str)
            return save_users(users)
    return False

# *** NEW: Function to remove a leave date for a user. ***
def remove_leave_date(telegram_id, leave_date_str):
    """Removes a leave date (YYYY-MM-DD) for a specific user."""
    users = load_users()
    str_telegram_id = str(telegram_id)
    if str_telegram_id in users:
        if leave_date_str in users[str_telegram_id]['leave_dates']:
            users[str_telegram_id]['leave_dates'].remove(leave_date_str)
            return save_users(users)
    return False