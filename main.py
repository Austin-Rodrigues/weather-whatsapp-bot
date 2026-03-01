import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import config
from agents.weather_agent import handle_message

# Validate config on startup
config.validate_config()

# Initialize FastAPI app
app = FastAPI(title="WeatherBot", description="WhatsApp Weather Agent")

@app.get("/")
async def root():
    """Health check endpoint — confirms server is running."""
    return {"status": "WeatherBot is running!"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Webhook verification endpoint.
    Meta calls this when you register your webhook URL.
    It sends your verify token and expects it back.
    """
    params = dict(request.query_params)
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    print(f"🔐 Webhook verification attempt — mode: {mode}, token: {token}")
    
    # Check mode and token match what we expect
    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        print("✅ Webhook verified successfully!")
        return PlainTextResponse(content=challenge)
    else:
        print("❌ Webhook verification failed!")
        raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhook")
async def receive_message(request: Request):
    """
    Message receiving endpoint.
    Meta calls this every time a user sends your WhatsApp number a message.
    """
    try:
        data = await request.json()
        print(f"📩 Incoming webhook: {data}")
        
        # Meta sends a test ping when you register webhook — handle it
        if data.get("object") != "whatsapp_business_account":
            return {"status": "not a whatsapp message"}
        
        # Extract message details
        from services.whatsapp import extract_message
        success, sender, message = extract_message(data)
        
        if not success:
            # Could be a status update (delivered, read) not a message
            print(f"ℹ️ Non-message webhook received: {message}")
            return {"status": "ok"}
        
        print(f"📨 Message from {sender}: {message}")
        
        # Handle the message with our agent
        handle_message(sender, message)
        
        # Always return 200 quickly — Meta will retry if you don't
        return {"status": "ok"}
    
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        # Still return 200 to stop Meta from retrying
        return {"status": "ok"}


# Run server when executed directly
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WeatherBot server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)