import os.path
import pathlib
import json
import requests
from openai import OpenAI

CACHE_PATH = 'tmp.json'

def fetch(cache_path=CACHE_PATH, save_cache=True):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", # gpt-4o
        messages=[
          {"role": "system", "content": "You are a senior neuroscience PI, with a successful lab and historic career. You have received numerous NIH R01s and grant funding."},
          {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}]
        )
    content = completion.choices[0].message.content
    
    if save_cache:
        json.dump(content, open(cache_path, 'w'))
    return content

if __name__ == '__main__':
    fetch()
