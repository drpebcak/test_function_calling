from anthropic import Anthropic
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from claude3.bob import main
client = Anthropic()

main.run(client, model="claude-3-opus-20240229")
