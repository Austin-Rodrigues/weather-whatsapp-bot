import sys
import os

# Add root directory to Python path so config.py can be found
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic
import config

# Initialize the Anthropic client once
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

def call_claude(prompt):
    """
    Send a prompt to Claude and get a response.
    
    Args:
        prompt (str): The question or instruction for Claude
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Fast and cheap, perfect for this use case
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return True, message.content[0].text
    
    except anthropic.AuthenticationError:
        return False, "Invalid Anthropic API key — check your .env file"
    
    except anthropic.RateLimitError:
        return False, "Anthropic rate limit hit — please try again shortly"
    
    except Exception as e:
        return False, f"Error calling Claude: {str(e)}"


# Test when run directly
if __name__ == "__main__":
    print("🧪 Testing Claude connection...")
    success, response = call_claude("Reply with exactly: Claude is working!")
    
    if success:
        print(f"✅ Claude responded: {response}")
    else:
        print(f"❌ Failed: {response}")