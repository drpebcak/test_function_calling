import os
import sys

from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.abusive_factorial import main

api_key = os.environ["MISTRAL_API_KEY"]
endpoint = os.environ["MISTRAL_ENDPOINT"]
client = OpenAI(base_url=endpoint + "/v1", api_key=api_key)

main.run(client, model="gpt-3.5-turbo")
