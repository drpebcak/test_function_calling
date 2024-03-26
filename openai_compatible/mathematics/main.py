import json

from openai import OpenAI

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


def run(client: OpenAI, model: str, test: str = None):
    messages = []
    messages.append({
        "role": "system",
        "content": base_system_prompt + "\n"
    })

    if test == "addition":
        messages.append({
            "role": "user",
            "content": "What is four plus five?"
        })
    elif test == "subtraction":
        messages.append({
            "role": "user",
            "content": "What is ten minus two?"
        })
    elif test == "multiplication":
        messages.append({
            "role": "user",
            "content": "What is six times seven?"
        })
    elif test == "division":
        messages.append({
            "role": "user",
            "content": "What is twenty divided by four?"
        })
    elif test == "parallel":
        messages.append({
            "role": "user",
            "content": "What is four plus five? What is ten minus two? What is six times seven? What is twenty divided by four?"
        })
    elif test == "duplicate":
        messages.append({
            "role": "user",
            "content": "What is four plus five? What is 3 plus two?"
        })
    elif test == "chaining": # This example of chaining can lead to hallucination
        messages.append({
            "role": "user",
            "content": "What is four plus six? What is the result of that plus 2? Take the result and multiply by 5 and then divide by two."
        })

    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'addition',
                'description': "Adds two numbers together",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'a': {
                            'description': 'First number to add',
                            'type': 'string'
                        },
                        'b': {
                            'description': 'Second number to add',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'subtraction',
                'description': "Subtracts two numbers",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'a': {
                            'description': 'First number',
                            'type': 'string'
                        },
                        'b': {
                            'description': 'Number to subtract',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'multiplication',
                'description': "Multiply two numbers together",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'a': {
                            'description': 'First number to multiply',
                            'type': 'string'
                        },
                        'b': {
                            'description': 'Second number to multiply',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'division',
                'description': "Divide two numbers",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'a': {
                            'description': 'First number to use as the dividend',
                            'type': 'string'
                        },
                        'b': {
                            'description': 'Second number to use as the divisor',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        }
    ]

    result = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto'
    )

    while result.choices[0].finish_reason == "tool_calls":
        messages.append(result.choices[0].message)
        # print("MESSAGES: ",messages)
        result = process_tool_call(client, result, model, messages, tools)

    # print(result)
    print(result.choices[0].message.content)

def process_tool_call(client: OpenAI, response, model: str, messages: list, tools: list):
    for tool in response.choices[0].message.tool_calls:
        if tool.function.name == "addition":
            messages.append({
                "role": "tool",
                "name": "addition",
                "content": add(tool.function.arguments),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "subtraction":
            messages.append({
                "role": "tool",
                "name": "subtraction",
                "content": sub(tool.function.arguments),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "multiplication":
            messages.append({
                "role": "tool",
                "name": "multiplication",
                "content": mult(tool.function.arguments),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "division":
            messages.append({
                "role": "tool",
                "name": "division",
                "content": div(tool.function.arguments),
                "tool_call_id": tool.id
            })

    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto'
    )


def add(args: str):
    args = json.loads(args)
    return str(int(args["a"]) + int(args["b"]))


def sub(args: str):
    args = json.loads(args)
    return str(int(args["a"]) - int(args["b"]))


def mult(args: str):
    args = json.loads(args)
    return str(int(args["a"]) * int(args["b"]))


def div(args: str):
    args = json.loads(args)
    return str(int(args["a"]) / int(args["b"]))
