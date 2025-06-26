# notifier.py
import sys
import requests

# --- Configuration ---
BOT_TOKEN = "7783964471:AAHIkKcVIRGfqxDDBjLRwtXnlcni8Kd2-yk"
GROUP_CHAT_ID = "-1002793378249"

def send_notification(message):
    """Sends a message to the Telegram group using the HTTP API."""
    # Using the requests library is simple and avoids conflicts with the async bot.
    # The URL is for the sendMessage method of the Telegram Bot API.
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # The payload contains the chat ID and the message text.
    # parse_mode="Markdown" allows for text formatting like *bold* and _italic_.
    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        # Make the POST request to the Telegram API.
        response = requests.post(url, json=payload)
        # Check if the request was successful.
        if response.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Failed to send notification. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"An exception occurred while sending notification: {e}")

if __name__ == "__main__":
    # This allows us to run the script from the command line,
    # passing the message as an argument.
    if len(sys.argv) > 1:
        # Join all arguments to form the message string.
        message_to_send = " ".join(sys.argv[1:])
        send_notification(message_to_send)