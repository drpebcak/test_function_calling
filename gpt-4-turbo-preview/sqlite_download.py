from openai import OpenAI
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from openai_compatible.generative_tools.sqlite_download import main
from openai_compatible import API_KEY, BASE_URL

client = OpenAI(api_key=API_KEY,
                base_url= BASE_URL)

main.run(client, model="gpt-4-turbo-preview")
