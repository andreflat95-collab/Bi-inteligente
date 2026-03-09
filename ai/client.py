from openai import OpenAI
import os

def get_client():
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

