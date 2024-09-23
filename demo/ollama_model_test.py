import ollama

model_name = 'jarvis_model'

prompt = """
What's your name?
""".strip()

response = ollama.generate(
    model=model_name,
    prompt=prompt,
)

output = response.get('response')
print(output.strip())