from openai import OpenAI
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.generative_tools.sqlite_download import main
client = OpenAI()

main.run(client, model="gpt-4-turbo-preview")
