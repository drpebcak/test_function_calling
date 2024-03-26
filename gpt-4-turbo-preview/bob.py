from openai import OpenAI
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.bob import main
client = OpenAI(api_key="sk-xx",
                base_url="https://api.openai.com/v1/")
                # base_url= "http://localhost:8019/v1/")

main.run(client, model="gpt-4-turbo-preview")
