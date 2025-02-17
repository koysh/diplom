import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты — помощник, который создает краткие резюме текста."},
            {"role": "user", "content": f"Создай резюме для следующего текста: {text}"}
        ],
        max_tokens=500
    )
    
    summary = response['choices'][0]['message']['content']
    return summary
