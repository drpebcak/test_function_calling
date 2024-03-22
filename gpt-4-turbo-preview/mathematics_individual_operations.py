import os
import sys

from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.mathematics import main

client = OpenAI()

main.run(client, model="gpt-4-turbo-preview", test="addition")
main.run(client, model="gpt-4-turbo-preview", test="subtraction")
main.run(client, model="gpt-4-turbo-preview", test="multiplication")
main.run(client, model="gpt-4-turbo-preview", test="division")
