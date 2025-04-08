import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key from environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Function to get weather data (simulating an API call)


def get_weather(latitude, longitude):
    print(
        f"Fetching weather for coordinates: latitude={latitude}, longitude={longitude}")
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    print("Weather data fetched:", data)
    return data['current']['temperature_2m']


# Define the tool schema for the model
tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True},
    {
    "type": "web_search_preview",
    "search_context_size": "medium",
        "user_location": {
            "type": "approximate",
            "country": "US",  # Change this to your desired country code
            "city": "New York",  # Change this to your desired city
            "region": "New York",  # Change this to your desired region
        }
}]

# First call to the model
input_messages = [
    {"role": "user", "content": "What's the weather like in Hefei city, China today?"}]

response = client.responses.create(
    model="gpt-4o",  # Use the correct model
    input=input_messages,
    tools=tools,
    stream=True  # Enable streaming
)

# Initialize final tool calls to handle streamed responses
final_tool_calls = {}

# Handle streamed response and process each event
for event in response:
    # print("Streaming event:", event)

    if event.type == 'response.output_item.added':
        print("Function call added:", event)
        final_tool_calls[event.output_index] = event.item

    elif event.type == 'response.function_call_arguments.delta':
        print("Function call argument delta:", event)
        index = event.output_index

        if final_tool_calls.get(index):
            final_tool_calls[index].arguments += event.delta

    elif event.type == 'response.function_call_arguments.done':
        print("Function call arguments done:", event)

        # Once function call arguments are complete, execute the function
        tool_call = final_tool_calls[event.output_index]
        arguments = json.loads(tool_call.arguments)
        print(f"Executing function with arguments: {arguments}")

        # Execute the get_weather function to get the result
        result = get_weather(arguments["latitude"], arguments["longitude"])

        # Send the result back to the model for final output
        print(f"Sending function result back: {result}")

        # Append the result to the model's input with the correct call_id
        input_messages.append(tool_call)  # Append the function call message
        input_messages.append({
            "type": "function_call_output",
            "call_id": tool_call.call_id,  # Ensure call_id matches the tool call
            "output": str(result)
        })

        # Send the updated input messages to the model for the final response
        response_2 = client.responses.create(
            model="gpt-4o",  # Use the same model for final response
            input=input_messages,
            tools=tools,
        )

        # Process and print the final output response from the model
        print("Final streaming response:", response_2.output_text)
