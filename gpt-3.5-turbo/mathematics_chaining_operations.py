import os
import sys

from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.mathematics import main

client = OpenAI()

main.run(client, model="gpt-3.5-turbo", test="chaining")
