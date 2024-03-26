import os
import sys

from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.mathematics import main
from openai_compatible import API_KEY, BASE_URL

client = OpenAI(api_key=API_KEY,
                base_url= BASE_URL)

main.run(client, model="gpt-4-turbo-preview", test="chaining")
