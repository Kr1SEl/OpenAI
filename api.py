import openai
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import os
import re

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_SECRET")


def parse_image_text(chat_id):
    return pytesseract.image_to_string(Image.open(f"photos/{chat_id}.jpg"))


def ask_openAI(question, model):
    response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model=f"{model}",
        messages=[{"role": "user", "content": f"{question}"}]
    )
    out = f"```{substitute_string(question)}```\n{substitute_string(response.choices[0].message.content)}\n"
    # print(out)
    # out = f'{response.choices[0].message.content}'
    return out


def substitute_string(string):
    symbols_to_remove = [
        '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for symbol in symbols_to_remove:
        string = re.sub(re.escape(symbol), "\\"+symbol, string)
    print(string)
    return string
