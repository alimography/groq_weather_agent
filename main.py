from groq import Groq
from dotenv import load_dotenv
import requests
import os

load_dotenv()


groq_api_key = os.getenv("GROQ_API_KEY") 

client = Groq(api_key=groq_api_key)



def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"


def main():
    user_query = input("> ")
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            { "role": "user", "content": user_query }
        ]
    )

    print(f"🤖: {response.choices[0].message.content}")

main()