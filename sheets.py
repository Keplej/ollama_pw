import json
import ollama
from google_api import create_service
from dotenv import load_dotenv
import os

load_dotenv()

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

def construct_sheets_service():
    client_file = 'client_secret.json'
    API_NAME = 'sheets'
    API_VERSION = 'v4'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = create_service(client_file, API_NAME, API_VERSION, SCOPES)
    return service


def add_sheet_entry(service, spreadsheet_id, first_name, last_name, age):
    range_ = 'DataEntry!B:B'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_
    ).execute()
    values_in_column_b = result.get('values', [])
    last_row = len(values_in_column_b) + 1
    values = [first_name, last_name, age]
    body = {
        'values': [values]
    }
    response = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'DataEntry!B{last_row}:D{last_row}',
        valueInputOption='RAW',
        body=body
    ).execute()
    return response

def add_sheet_entry_tool():
    return {
        'type': 'function',
        'function': {
            'name': 'add_sheet_entry',
            'description': 'Add an entry to a Google Sheet',
            'properties': {
                'first_name': {
                    'type': 'string',
                    'description': 'The first name of the person'
                },
                'last_name': {
                    'type': 'string',
                    'description': 'The last name of the person'
                },
                'age': {
                    'type': 'integer',
                    'description': 'The age of the person'
                }
            },
            'required': ['first_name', 'last_name', 'age']
        }
    }

def system_prompt():
    return """
    Your job is to take a user input and add it to the Google Sheet and ensure that all the qeuried arguments are populated in the tool call.

    Required arguments for 'add_sheet_entry':
    - first_name
    - last_name
    - age

    If response is '{"entry_added": true}', reply with "entry added" to the user.

    Example of a correctly formatted tool call (dict):
    {
        'function': {
            'name': 'add_sheet_entry',
            'arguments': {
                'first_name': 'John',
                'last_name': 'Doe',
                'age': 30
            }
        }
    }
""".strip()

def run():
    model = 'llama3.1:8b'
    client = ollama.Client()
    spreadsheet_id = f'{SPREADSHEET_ID}'
    service = construct_sheets_service()
    messages = [
        {
            'role': 'system',
            'content': system_prompt()
        }
    ]

    # We will use a input to prompt the user to use the chat 
    # to continune the language
    while True:
        prompt = input("Enter the first name, last name, and age of the perosn (or 'exit' to quit): \n")
        if prompt.lower() == 'exit':
            print("Goodbye!")
            break

        messages.append({'role': 'user', 'content': prompt})

        # send a request using the chat method
        # Convert tools to the format expected by Ollama
        response = client.chat(
            model=model,
            messages=messages,
            tools=[add_sheet_entry_tool()]
        )
        messages.append(response['message'])

        # Process function calls made by the model
        if not response['message'].get('tool_calls'):
            print('The model didn\'t use the function, Its response was:')
            print(response['message']['content'])
            continue

        if response['message'].get('tool_calls'):
            available_functions = {
                'add_sheet_entry': add_sheet_entry,
            }

            for tool in response['message']['tool_calls']:
                function_to_call = available_functions[tool['function']['name']]
                function_response = function_to_call(**tool['function']['arguments'], service=service, spreadsheet_id=spreadsheet_id)
                # Add function response to the conversation

                messages.append(
                    {
                        'role': 'tool',
                        'content': '{"entry_added": true}'
                    }
                )
        final_response = client.chat(model=model, messages=messages, stream=False)
        messages.append(final_response['message'])
        print("Agent:", final_response['message']['content'])
        print('\n')

run()