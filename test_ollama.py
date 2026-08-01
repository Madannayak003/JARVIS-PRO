from ai.ollama import ask_ollama

response = ask_ollama(
    "You are helpful.",
    "Say hello."
)

print(response)