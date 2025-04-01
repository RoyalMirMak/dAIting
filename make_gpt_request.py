import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GPT_KEY_CHATGPT')
API_URL = os.getenv('LINK_CHATGPT')


def make_gpt_request(prompt, temperature=0.7, max_tokens=500, model_name="gpt-4o-mini-2024-07-18", system_message=""):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        raise Exception(f"API request failed: {response.status_code}, {response.text}")


# Example usage
"""
user_input = input("Введите ваш запрос: ")
bot_response = get_gpt_response(user_input)
print("Ответ от GPT:", bot_response)
"""
