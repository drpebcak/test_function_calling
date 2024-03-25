import os
import sys

from anthropic import Anthropic

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from claude3.generative_tools.sqlite_download import main

client = Anthropic()

main.run(client, model="claude-3-sonnet-20240229")
