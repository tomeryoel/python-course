from google import genai

client = genai.Client(api_key="AIzaSyC2ImI4i17_ZPZ7kwqDH0Qz3-GiXotJo0A")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What is the capital of France?",
)

print(response.text)