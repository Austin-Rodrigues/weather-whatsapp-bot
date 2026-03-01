import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import config

def get_coordinates_url(location):
    """
    Use Claude to generate NWS Points API URL for a location.
    Imported here to avoid circular imports.
    """
    from services.claude import call_claude
    
    prompt = f"""
You are an expert at working with the National Weather Service (NWS) API.

Your task: Generate the NWS API URL to get weather forecast data for "{location}".

Instructions:
1. Determine the approximate latitude and longitude coordinates for this location
2. Generate the NWS Points API URL: https://api.weather.gov/points/{{lat}},{{lon}}

Return ONLY the complete Points API URL, nothing else.
Format: https://api.weather.gov/points/LAT,LON
"""
    return call_claude(prompt)


def fetch_nws_data(url):
    """
    Fetch data from NWS API using requests.
    
    Args:
        url (str): NWS API URL to fetch
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        headers = {"User-Agent": config.NWS_USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return True, response.text
        else:
            return False, f"NWS API returned status {response.status_code}"
    
    except requests.Timeout:
        return False, "NWS API request timed out"
    
    except Exception as e:
        return False, f"Error fetching NWS data: {str(e)}"


def get_forecast_url(points_json):
    """
    Extract forecast URL from NWS Points API response.
    
    Args:
        points_json (str): JSON response from Points API
    
    Returns:
        tuple: (success: bool, forecast_url: str)
    """
    try:
        data = json.loads(points_json)
        forecast_url = data['properties']['forecast']
        return True, forecast_url
    
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Error parsing Points API response: {str(e)}"


def summarize_forecast(raw_json, location):
    """
    Use Claude to convert raw NWS JSON into readable summary.
    
    Args:
        raw_json (str): Raw forecast JSON from NWS
        location (str): Original location for context
    
    Returns:
        tuple: (success: bool, summary: str)
    """
    from services.claude import call_claude
    
    prompt = f"""
You are a weather assistant responding via WhatsApp.
Convert this NWS forecast data for "{location}" into a concise, friendly summary.

Keep it under 500 words and use simple formatting suitable for WhatsApp:
- Use emojis for weather conditions
- Bold key information with *asterisks*
- Keep sentences short and clear

Raw NWS Data:
{raw_json}

Include: current conditions, today's forecast, next 2 days outlook, any alerts.
"""
    return call_claude(prompt)


def get_weather(location):
    """
    Main weather function — orchestrates all NWS API calls.
    This is the only function other files need to call.
    
    Args:
        location (str): Location to get weather for
    
    Returns:
        tuple: (success: bool, weather_summary: str)
    """
    print(f"🌤️ Getting weather for: {location}")
    
    # Step 1: Get coordinates URL from Claude
    success, points_url = get_coordinates_url(location)
    if not success:
        return False, f"Failed to generate API URL: {points_url}"
    
    points_url = points_url.strip()
    if not points_url.startswith('https://api.weather.gov/points/'):
        return False, f"Invalid URL generated: {points_url}"
    print(f"✅ Points URL: {points_url}")
    
    # Step 2: Fetch points data
    success, points_data = fetch_nws_data(points_url)
    if not success:
        return False, f"Failed to fetch location data: {points_data}"
    print(f"✅ Got points data")
    
    # Step 3: Extract forecast URL
    success, forecast_url = get_forecast_url(points_data)
    if not success:
        return False, f"Failed to extract forecast URL: {forecast_url}"
    print(f"✅ Forecast URL: {forecast_url[:60]}...")
    
    # Step 4: Fetch forecast data
    success, forecast_data = fetch_nws_data(forecast_url)
    if not success:
        return False, f"Failed to fetch forecast: {forecast_data}"
    print(f"✅ Got forecast data")
    
    # Step 5: Summarize with Claude
    success, summary = summarize_forecast(forecast_data, location)
    if not success:
        return False, f"Failed to summarize forecast: {summary}"
    print(f"✅ Summary generated")
    
    return True, summary


# Test when run directly
if __name__ == "__main__":
    print("🧪 Testing weather service...")
    success, result = get_weather("New York City")
    
    if success:
        print("\n📋 Weather Summary:")
        print("=" * 50)
        print(result)
        print("=" * 50)
    else:
        print(f"❌ Failed: {result}")