import os

openai_base_url = "https://api.openai.com/v1/"
API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("BASE_URL", openai_base_url)

if BASE_URL != openai_base_url:
    print(f"Pointing to Local Base URL: {BASE_URL}")
else: # check if the openAI API key is set
    if API_KEY == "":
        raise Exception("Please set your OpenAI API key as an environment variable: OPENAI_API_KEY")

