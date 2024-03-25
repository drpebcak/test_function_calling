import os
import sys

from anthropic import Anthropic

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from claude3.mathematics import main

client = Anthropic()

main.run(client, model="claude-3-haiku-20240307", test="duplicate")
