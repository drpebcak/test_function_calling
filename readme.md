# Test Function Calling

```bash
python -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```



## Get Started with OpenAI GPT4
Set OpenAI API KEY:
```bash
export OPENAI_API_KEY=sk-xxx
```

then run:
```bash
python gpt-4-turbo-preview/bob.py
```

(Optional) If you set the `BASE_URL` to local model and want to back to use OpenAI, please do:
```
 export BASE_URL=https://api.openai.com/v1/
```

## Use Rubra -- OpenAI Compatible Local LLM Server
Simply set the `BASE_URL` to point to the local server.
```bash
export BASE_URL=http://localhost:8019/v1/
```

then run:
```bash
python gpt-4-turbo-preview/bob.py
```

### How to run the Local Model?
1. git clone the repo and make to build the server:
```bash
git clone https://github.com/tybalex/function.cpp.git
cd function.cpp 
make
```

2. Download the Quantized Local LLM from huggingface: https://huggingface.co/yingbei/rubra-9b-rc1/tree/main
```bash
wget https://huggingface.co/yingbei/rubra-9b-rc1/resolve/main/rubra-9b-rc1.gguf
```

3. Start the server. Change the port number if you want.
```bash
./server -ngl 99 -m rubra-9b-rc1.gguf  --port 8019 --host 0.0.0.0  -c 8192 --chat-template llama2
```

Model will get updated in the future.
