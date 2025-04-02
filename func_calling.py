import argparse
import ollama
import yfinance as yf
from typing import Dict, Any, Callable
from ollama import chat, ChatResponse
import requests
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo

# Tools and helper functions


def get_disk_usage():
    """Retrieves disk usage."""
    path = r"C:\\"
    total, used, free = shutil.disk_usage(path)
    gb = 1024 * 1024 * 1024
    return {
        "total": f"{total / gb:.2f} GB",
        "used": f"{used / gb:.2f} GB",
        "free": f"{free / gb:.2f} GB",
    }


def get_current_time(location: str) -> str:
    """Retrieve current time for a given location."""
    # Mapping of common locations to their timezone identifiers
    location_timezones = {
        "beijing": "Asia/Shanghai",
        "dhaka": "Asia/Dhaka",
        "new york": "America/New_York",
        "london": "Europe/London",
        # Add more mappings as needed
    }
    tz_name = location_timezones.get(location.lower())
    if not tz_name:
        raise Exception(f"Timezone for location '{location}' not found")
    now = datetime.now(ZoneInfo(tz_name))
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


def subtract_two_numbers(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


def get_stock_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    price_attrs = ['regularMarketPrice', 'currentPrice', 'price']
    for attr in price_attrs:
        if attr in ticker.info and ticker.info[attr] is not None:
            return ticker.info[attr]
    fast_info = ticker.fast_info
    if hasattr(fast_info, 'last_price') and fast_info.last_price is not None:
        return fast_info.last_price
    raise Exception("Could not find valid price data")


# Manual tool definitions
add_two_numbers_tool = {
    'type': 'function',
    'function': {
        'name': 'add_two_numbers',
        'description': 'Add two numbers',
        'parameters': {
            'type': 'object',
            'required': ['a', 'b'],
            'properties': {
                'a': {'type': 'integer', 'description': 'The first number'},
                'b': {'type': 'integer', 'description': 'The second number'},
            },
        },
    },
}

subtract_two_numbers_tool = {
    'type': 'function',
    'function': {
        'name': 'subtract_two_numbers',
        'description': 'Subtract two numbers',
        'parameters': {
            'type': 'object',
            'required': ['a', 'b'],
            'properties': {
                'a': {'type': 'integer', 'description': 'The first number'},
                'b': {'type': 'integer', 'description': 'The second number'},
            },
        },
    },
}

get_stock_price_tool = {
    'type': 'function',
    'function': {
        'name': 'get_stock_price',
        'description': 'Get the current stock price for any symbol',
        'parameters': {
            'type': 'object',
            'required': ['symbol'],
            'properties': {
                'symbol': {'type': 'string', 'description': 'The stock symbol (e.g., AAPL, GOOGL)'},
            },
        },
    },
}

disk_usage_tool = {
    'type': 'function',
    'function': {
        'name': 'get_disk_usage',
        'description': 'Retrieve disk usage information',
        'parameters': {
            'type': 'object',
            'properties': {},
        },
    },
}

get_current_time_tool = {
    'type': 'function',
    'function': {
        'name': 'get_current_time',
        'description': 'Get the current time for a given location',
        'parameters': {
            'type': 'object',
            'required': ['location'],
            'properties': {
                'location': {'type': 'string', 'description': 'The location name (e.g., Beijing, London)'},
            },
        },
    },
}


def main():
    parser = argparse.ArgumentParser(
        description="Interact with llama3.1 model using a command line prompt")
    parser.add_argument("--prompt", type=str, required=True,
                        help="The prompt question to ask the model")
    args = parser.parse_args()

    print("Prompt:", args.prompt)

    # Map function names to functions for tool call processing
    available_functions: Dict[str, Callable] = {
        'request': requests.request,
        'add_two_numbers': add_two_numbers,
        'subtract_two_numbers': subtract_two_numbers,
        'get_stock_price': get_stock_price,
        'get_disk_usage': get_disk_usage,
        'get_current_time': get_current_time,
    }

    # Define the list of tools to offer to the LLM.
    tools = [
        add_two_numbers_tool,
        subtract_two_numbers_tool,
        get_stock_price_tool,
        disk_usage_tool,
        get_current_time_tool,
    ]

    # Sending the prompt to llama3.1 with the selected tools.
    # (You can add tools like requests.request as needed.)
    response: ChatResponse = ollama.chat(
        'llama3.1',
        messages=[{'role': 'user', 'content': args.prompt}],
        tools=[requests.request] + tools,
    )

    # Print the model's base content reply.
    if response.message.content:
        print("Response:", response.message.content)

    # Process any tool calls made by the model.
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            func = available_functions.get(tool_call.function.name)
            if func:
                print("Calling function:", tool_call.function.name)
                print("Arguments:", tool_call.function.arguments)
                output = func(**tool_call.function.arguments)
                print("Function output:", output)
            else:
                print("Function not found:", tool_call.function.name)


if __name__ == "__main__":
    main()
