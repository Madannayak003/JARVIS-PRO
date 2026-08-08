from ai.core.service import ai_service


response = ai_service.generate(

    prompt="Say hello.",

    system_prompt="You are a helpful assistant.",

    capability="conversation",

)


print("Provider:", response.provider)
print("Model:", response.model)
print("Success:", response.success)
print("Response:")
print(response.text)