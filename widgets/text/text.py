import os.path
import pathlib
import json
import requests
from openai import OpenAI

CUR_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.abspath(os.path.join(CUR_DIR, '..', 'cache'))
CACHE_PATH = os.path.join(CACHE_DIR, 'text.json')

def is_cached(cache_path=CACHE_PATH):
    return os.path.exists(cache_path)

def load_cached(cache_path=CACHE_PATH):
    return json.load(open(cache_path))

def fetch(cache_path=CACHE_PATH, save_cache=True):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
          {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
          {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}]
        )
    content = completion.choices[0].message.content
    
    if save_cache:
        json.dump(content, open(cache_path, 'w'))
    return content

def main(cached=True):
    if cached and is_cached():
        content = load_cached()
    else:
        content = fetch()

if __name__ == '__main__':
    main(cached=True)
