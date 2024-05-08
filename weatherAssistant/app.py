import os
import json
import requests
import streamlit as st
from groq import Groq

# set Groq and open weather api key:

GROQ_API_KEY = ""
OPENWEATHER_API_KEY = ""

# Create a Groq client:

client = Groq(api_key=GROQ_API_KEY)

#  Define Function:
def get_current_weather(location):
    """Get the current weather in a given location"""
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={OPENWEATHER_API_KEY}&q={location}"
    response = requests.get(complete_url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['main']
        temperature = data['main']['temp'] - 273.15  # Convert Kelvin to Celsius
        return {
            "city": location,
            "weather": weather,
            "temperature": round(temperature, 2)
        }
    else:
        return {"city": location, "weather": "Data Fetch Error", "temperature": "N/A"}


# Define a function as a tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

def main():
    st.title("Weather Assistant")

    location = st.text_input("Enter a location:")

    if st.button("Get Weather"):
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": f"What is the weather like in {location}?"
                }
            ],
            temperature=0,
            max_tokens=300,
            tools=tools,
            tool_choice="auto"
        )

        groq_response = response.choices[0].message

        #  get the arguments:
        args = json.loads(groq_response.tool_calls[0].function.arguments)
        weather_data = get_current_weather(**args)

        st.subheader(f"Weather in {weather_data['city']}:")
        st.write(f"Weather: {weather_data['weather']}")
        st.write(f"Temperature: {weather_data['temperature']}°C")

if __name__ == "__main__":
    main()