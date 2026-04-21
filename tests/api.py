from google import genai

client = genai.Client(api_key="")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Responda em uma frase: O que é uma API?"
)
print(response.text)