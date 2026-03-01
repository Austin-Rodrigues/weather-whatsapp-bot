import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import config

def send_message(to, message):
    """
    Send a WhatsApp message to a user.
    
    Args:
        to (str): Recipient's phone number (with country code, no +)
        message (str): Message text to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        url = f"https://graph.facebook.com/v18.0/{config.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {config.WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return True, "Message sent successfully"
        else:
            return False, f"Failed to send message: {response.status_code} - {response.text}"
    
    except Exception as e:
        return False, f"Error sending WhatsApp message: {str(e)}"


def extract_message(webhook_data):
    """
    Extract message text and sender from WhatsApp webhook payload.
    
    Args:
        webhook_data (dict): Raw webhook data from Meta
    
    Returns:
        tuple: (success: bool, sender: str, message: str)
    """
    try:
        entry = webhook_data['entry'][0]
        change = entry['changes'][0]
        value = change['value']
        
        # Check if this is actually a message
        if 'messages' not in value:
            return False, None, "No message in payload"
        
        message = value['messages'][0]
        sender = message['from']
        
        # Handle text messages only for now
        if message['type'] != 'text':
            return False, sender, "Sorry, I can only process text messages right now!"
        
        text = message['text']['body']
        return True, sender, text
    
    except (KeyError, IndexError) as e:
        return False, None, f"Error parsing webhook: {str(e)}"


def send_welcome_message(to):
    """Send a welcome/help message to a new user."""
    message = (
        "👋 *Welcome to WeatherBot!*\n\n"
        "I can get you weather forecasts for any location in the US.\n\n"
        "Just send me a location like:\n"
        "• *New York City*\n"
        "• *Los Angeles, CA*\n"
        "• *Chicago*\n\n"
        "What location would you like weather for? 🌤️"
    )
    return send_message(to, message)


# Test when run directly
if __name__ == "__main__":
    print("🧪 Testing WhatsApp service...")
    
    # Replace with your actual WhatsApp number for testing
    test_number = input("Enter your WhatsApp number (with country code, no +): ").strip()
    
    success, response = send_message(
        test_number,
        "✅ WeatherBot is connected and working!"
    )
    
    if success:
        print(f"✅ Message sent successfully!")
        print("Check your WhatsApp!")
    else:
        print(f"❌ Failed: {response}")

