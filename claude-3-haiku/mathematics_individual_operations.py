import os
import sys

from anthropic import Anthropic

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from claude3.mathematics import main

client = Anthropic()

main.run(client, model="claude-3-haiku-20240307", test="addition")
main.run(client, model="claude-3-haiku-20240307", test="subtraction")
main.run(client, model="claude-3-haiku-20240307", test="multiplication")
main.run(client, model="claude-3-haiku-20240307", test="division")
