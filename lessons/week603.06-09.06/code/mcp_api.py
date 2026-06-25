# import requests
# import json
# from google import genai

# # 1. Initialize Gemini client
# client = genai.Client(api_key="MY_API_KEY")  # Replace with your Gemini API key
# MODEL = "gemini-3.5-flash"

# # 2. Define available tool
# TOOLS = {
#     "get_weather": {
#         "description": "Get current weather for a city using Open-Meteo API",
#         "parameters": {"city": "string"}
#     }
# }

# # 3. Implement real API call
# def get_weather(city):
#     geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
#     geo_resp = requests.get(geo_url).json()

#     if "results" not in geo_resp or not geo_resp["results"]:
#         return f"Could not find coordinates for {city}."

#     lat = geo_resp["results"][0]["latitude"]
#     lon = geo_resp["results"][0]["longitude"]
#     country = geo_resp["results"][0].get("country", "Unknown")

#     weather_url = (
#         f"https://api.open-meteo.com/v1/forecast?"
#         f"latitude={lat}&longitude={lon}&current_weather=true"
#     )
#     weather_resp = requests.get(weather_url).json()

#     if "current_weather" not in weather_resp:
#         return f"No weather data available for {city}."

#     current = weather_resp["current_weather"]
#     temperature = current["temperature"]
#     windspeed = current["windspeed"]

#     return f"The current temperature in {city}, {country} is {temperature}Â°C with wind speed {windspeed} km/h."

# # 4. Run the agent
# def run_agent(user_input):
#     # Step 1: Ask Gemini which tool to use
#     system_prompt = (
#         "You are an AI agent that can use the following tools via MCP:\n"
#         + json.dumps(TOOLS, indent=2)
#         + "\nIf a tool is needed, respond ONLY in JSON as:\n"
#         + '{"tool": "tool_name", "arguments": {...}}\n'
#         + "Otherwise, answer directly.\n"
#         + f"User: {user_input}"
#     )

#     response = client.models.generate_content(model=MODEL, contents=system_prompt)
#     model_text = response.text.strip()
#     print(f"\nModel raw output:\n{model_text}\n")

#     # Step 2: Try parsing as JSON
#     try:
#         decision = json.loads(model_text)
#         tool = decision["tool"]
#         args = decision.get("arguments", {})
#     except Exception:
#         print("AI:", model_text)
#         return

#     # Step 3: Execute tool
#     print(f"Model requested tool: {tool}({args})")

#     if tool == "get_weather":
#         result = get_weather(args.get("city", ""))
#     else:
#         result = f"Unknown tool: {tool}"

#     # Step 4: Natural follow-up answer
#     followup = (
#         f"The user asked: '{user_input}'. "
#         f"The tool '{tool}' returned this result: '{result}'. "
#         "Now, respond to the user in a friendly, natural way. "
#         "Do not use JSON. Just write text."
#     )

#     final = client.models.generate_content(model=MODEL, contents=followup)
#     print("AI:", final.text.strip())


# # 5. Main loop
# if __name__ == "__main__":
#     print("MCP + Gemini 3.5 Real Weather API Demo\nType 'exit' to quit.")
#     while True:
#         user_input = input("\nYou: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         run_agent(user_input)
import requests
import json
import time

# 1. Configuration 
# ×©×™× ×¤×” ××ª ×”×ž×¤×ª×— ×”××ž×™×ª×™ ×©×œ×š ×©×ž×ª×—×™×œ ×‘-YOUR_GCP_API_KEY_HERE
API_KEY = "MY_API_KEY" 
MODEL = "gemini-2.5-flash" 

# 2. Define available tools (Changed back to location for user flexibility)
TOOLS = {
    "get_weather": {
        "description": "Get current weather for a city using Open-Meteo API",
        "parameters": {"city": "string"}
    },
    "get_current_time": {
        "description": "Get the current live local time and date for any city or location in the world.",
        "parameters": {"location": "string"}
    }
}

# 3. Helper function to call Gemini directly via REST API
def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Gemini API Error {response.status_code}: {response.text}")
            return "Error communicating with Gemini."
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Request failed: {str(e)}"

# 4. Implement real API functions
def get_weather(city):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    try:
        geo_resp = requests.get(geo_url).json()
        if "results" not in geo_resp or not geo_resp["results"]:
            return f"Could not find coordinates for {city}."
        
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        country = geo_resp["results"][0].get("country", "Unknown")

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url).json()
        
        current = weather_resp["current_weather"]
        return f"The current temperature in {city}, {country} is {current['temperature']}Â°C with wind speed {current['windspeed']} km/h."
    except Exception:
        return f"Error retrieving weather data for {city}."


def get_current_time(location):
    # Step A: Get coordinates using Open-Meteo Geocoding (Very reliable)
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}"
    try:
        geo_resp = requests.get(geo_url).json()
        if "results" not in geo_resp or not geo_resp["results"]:
            return f"Could not find coordinates for location: '{location}'."
        
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        city_name = geo_resp["results"][0]["name"]
        country = geo_resp["results"][0].get("country", "Unknown")

        # Step B: Call Google Time Zone API using your API_KEY
        # We need the current timestamp to let Google calculate Daylight Saving Time (DST) correctly
        current_timestamp = int(time.time())
        google_time_url = (
            f"https://maps.googleapis.com/maps/api/timezone/json"
            f"?location={lat},{lon}"
            f"&timestamp={current_timestamp}"
            f"&key={API_KEY}"
        )
        
        time_resp = requests.get(google_time_url).json()
        
        if time_resp.get("status") == "OK":
            # Calculate local time based on UTC time + rawOffset + dstOffset
            # google gives offsets in seconds, we convert to local timestamp
            local_timestamp = current_timestamp + time_resp["rawOffset"] + time_resp["dstOffset"]
            
            # Convert timestamp to a readable time format (HH:MM) and date
            local_struct_time = time.gmtime(local_timestamp)
            readable_time = time.strftime("%H:%M", local_struct_time)
            readable_date = time.strftime("%Y-%m-%d", local_struct_time)
            timezone_name = time_resp.get("timeZoneName", "")

            return f"The current live time in {city_name}, {country} ({timezone_name}) is {readable_time} and the date is {readable_date}."
        
        elif time_resp.get("status") == "REQUEST_DENIED":
            # If Time Zone API is not enabled yet in your AI Studio/GCP Console, we use a fallback!
            # Let's use a bulletproof fallback to a generic time API if Google is denied
            return get_time_fallback(lat, lon, city_name, country)
        else:
            return f"Google Time API returned status: {time_resp.get('status')}"
            
    except Exception as e:
        return f"Failed to fetch time due to an error: {str(e)}"

# Bulletproof fallback in case Google TimeZone API is not toggled 'ON' in the dashboard
def get_time_fallback(lat, lon, city_name, country):
    fallback_url = f"https://timeapi.io/api/time/current/coordinate?latitude={lat}&longitude={lon}"
    try:
        # Using a direct GET now to avoid POST issues
        resp = requests.get(fallback_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return f"The current time in {city_name}, {country} is {data['time']} and the date is {data['date']}."
    except:
        pass
    return f"Could not calculate time for {city_name} (Google API and Fallback both unavailable)."


# 5. Run the agent
def run_agent(user_input):
    # Step 1: Ask Gemini which tool to use
    system_prompt = (
        "You are an AI agent that can use the following tools:\n"
        + json.dumps(TOOLS, indent=2)
        + "\nIf a tool is needed, respond ONLY in JSON as:\n"
        + '{"tool": "tool_name", "arguments": {...}}\n'
        + "Otherwise, answer directly.\n"
        + f"User: {user_input}"
    )

    model_text = call_gemini(system_prompt).strip()
    print(f"\nModel raw output:\n{model_text}\n")

    # Step 2: Try parsing as JSON
    try:
        if model_text.startswith("```json"):
            model_text = model_text.split("```json")[1].split("```")[0].strip()
        elif model_text.startswith("```"):
            model_text = model_text.split("```")[1].split("```")[0].strip()
            
        decision = json.loads(model_text)
        tool = decision["tool"]
        args = decision.get("arguments", {})
    except Exception:
        print("AI:", model_text)
        return

    # Step 3: Execute tool
    print(f"Model requested tool: {tool}({args})")

    if tool == "get_weather":
        result = get_weather(args.get("city", ""))
    elif tool == "get_current_time":
        # Changed parameter key back to 'location' to match the updated TOOLS
        result = get_current_time(args.get("location", "")) 
    else:
        result = f"Unknown tool: {tool}"

    # Step 4: Natural follow-up answer
    followup = (
        f"The user asked: '{user_input}'. "
        f"The tool '{tool}' returned this result: '{result}'. "
        f"Now, respond to the user in a friendly, natural way (in the language the user used). "
        "Do not use JSON. Just write text."
    )

    final_text = call_gemini(followup)
    print("AI:", final_text.strip())


# 6. Main loop
if __name__ == "__main__":
    print("MCP + Gemini Real Weather & Time API Demo (REST Version)\nType 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        run_agent(user_input)

