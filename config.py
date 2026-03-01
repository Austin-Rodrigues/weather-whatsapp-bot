import os
from dotenv import load_dotenv

# Explicitly find .env file from root directory
# This works no matter where the file is called from
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# WhatsApp
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

# NWS
NWS_USER_AGENT = os.getenv("NWS_USER_AGENT", "WeatherBot/1.0")

# Validate all critical variables are present
def validate_config():
    missing = []
    
    if not ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not WHATSAPP_TOKEN:
        missing.append("WHATSAPP_TOKEN")
    if not WHATSAPP_PHONE_NUMBER_ID:
        missing.append("WHATSAPP_PHONE_NUMBER_ID")
    if not WHATSAPP_VERIFY_TOKEN:
        missing.append("WHATSAPP_VERIFY_TOKEN")
    
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    print("✅ All environment variables loaded successfully")

# Run validation when file is executed directly
if __name__ == "__main__":
    validate_config()