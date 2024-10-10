# ollama_pw

## Demo
- The Demo file is a basic run down on how you can customize your modelfile and have your own AI versions.

### Demo Instructions
- First go to https://ollama.com/ and download the LLM along with running the command `pip install ollama` in your project folder
- In a command prompt terminal run the command `ollama` to see if you have it install correctly. It will show a set of commands
- run the command in the command prompt terminal `ollama pull <model version you want goes here>`
    - To install a specific model check the ollama website library at https://ollama.com/library

## Weather
- This section is to learn and show off function calling with APIs Ollama AI
- Weather is requesting data from the openweathermap api and we are displaying the information with the ollama api model llama3.1

### Weather Instructions
- Go create an account for free at https://openweathermap.org/ and create an api key
- Open up a cmd and run run the command `ollama pull llama3.1:8b` as this is the model that was used for the weather
    - To change the model go to line 58 in `weather.py`: `model = 'llama3.1:8b'`
- Create a .env file and put your API_KEY from openweathermap to use the api with the llama3.1 LLM AI

## Sheets


### Sheets Instructions