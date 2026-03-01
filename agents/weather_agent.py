import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.weather import get_weather
from services.whatsapp import send_message, send_welcome_message

# Simple in-memory store to track conversation state
# Stores what step each user is on
user_sessions = {}

def handle_message(sender, message):
    """
    Main agent function — handles incoming WhatsApp messages.
    Decides what to do based on message content and user history.
    
    Args:
        sender (str): User's WhatsApp number
        message (str): Message text from user
    
    Returns:
        tuple: (success: bool, response: str)
    """
    print(f"📨 Message from {sender}: {message}")
    
    message_lower = message.lower().strip()
    
    # Handle greetings — send welcome message
    if message_lower in ['hi', 'hello', 'hey', 'start', 'help']:
        success, response = send_welcome_message(sender)
        return success, response
    
    # Handle thank you
    if message_lower in ['thanks', 'thank you', 'ty', 'thx']:
        success, response = send_message(
            sender,
            "You're welcome! 😊 Send me any US location for another forecast!"
        )
        return success, response
    
    # Everything else — treat as a location query
    print(f"🌤️ Processing weather request for: {message}")
    
    # Send acknowledgment first so user knows we're working
    send_message(sender, f"🔍 Looking up weather for *{message}*... Please wait!")
    
    # Get weather
    success, weather_summary = get_weather(message)
    
    if success:
        send_message(sender, weather_summary)
        return True, "Weather sent successfully"
    else:
        error_message = (
            f"❌ Sorry, I couldn't get weather for *{message}*.\n\n"
            "Please try:\n"
            "• A city name: *Chicago*\n"
            "• City and state: *Austin, TX*\n"
            "• Only US locations are supported"
        )
        send_message(sender, error_message)
        return False, weather_summary


# Test when run directly
if __name__ == "__main__":
    print("🧪 Testing weather agent...")
    
    test_number = input("Enter your WhatsApp number (with country code, no +): ").strip()
    
    print("\nTest 1: Greeting")
    handle_message(test_number, "hello")
    
    input("\nPress Enter to test weather query...")
    
    print("\nTest 2: Weather Query")
    handle_message(test_number, "New York City")
    
    print("\n✅ Agent test complete — check your WhatsApp!")