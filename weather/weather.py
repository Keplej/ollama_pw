import json
import httpx
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

weather_api = os.getenv('API_KEY')


def get_weather(city, api_key):
    base_url = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'imperial'
    }

    try:
        response = httpx.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # can modify to what specific data you want from ai agent
        json_response = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'wind_speed': data['wind']['speed'],
        }
        return json.dumps(json_response)
    except httpx.RequestError as e:
        return json.dumps({'error': f'Failed to fetch weather data: {str(e)}'})
    
# 
def get_weather_tool():
    return {
        'type': 'function', # tool type as function. In general LLM has 3 tool types: File search, code interpreter, and function calling
        'function': { # required field
            'name': 'get_weather',
            'description': 'Get the current weather for a city',
            'properties': {
                'city': {
                    'type': 'string',
                    'description': 'The city to get the weather for'
                }
            },
            'required': ['city']
        }
    }

# This is the entry point
def run():
    model = 'llama3.1:8b'
    client = ollama.Client()
    messages = [
        {
            'role': 'system',
            'content': 'If message is a json object in string format, it will be parsed and displayed as a sentence'
        }
    ]

    # We will use a input to prompt the user to use the chat 
    # to continune the language
    while True:
        prompt = input("Ask me about the weather (type the city name or 'exit' to quit): ")
        if prompt.lower() == 'exit':
            break

        messages.append({'role': 'user', 'content': prompt})

        # send a request using the chat method
        response = client.chat(
            model=model,
            messages=messages,
            tools=[get_weather_tool()]
        )
        messages.append(response['message'])

        # 
        if not response['message'].get('tool_calls'):
            print('The model didn\'t use the function, Its response was:')
            print(response['message']['content'])
            continue

        if response['message'].get('tool_calls'):
            available_functions = {
                'get_weather': get_weather,
            }

            for tool in response['message']['tool_calls']:
                function_to_call = available_functions[tool['function']['name']]
                function_response = function_to_call(tool['function']['arguments']['city'], API_KEY)
                # Add function response to the conversation

                messages.append(
                    {
                        'role': 'tool',
                        'content': function_response
                    }
                )
        final_response = client.chat(model=model, messages=messages)
        messages.append(final_response['message'])
        print(final_response['message']['content'])
        print('\n')


if __name__ == '__main__':
    API_KEY = weather_api
    run()
