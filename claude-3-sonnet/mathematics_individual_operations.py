import os
import sys

from anthropic import Anthropic

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from claude3.mathematics import main

client = Anthropic()

main.run(client, model="claude-3-sonnet-20240229", test="addition")
main.run(client, model="claude-3-sonnet-20240229", test="subtraction")
main.run(client, model="claude-3-sonnet-20240229", test="multiplication")
main.run(client, model="claude-3-sonnet-20240229", test="division")
