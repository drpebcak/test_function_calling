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

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'myfunction',
            'description': "A function taking an integer as argument and returns an integer",
            'parameters': {
                'type': 'object',
                'properties': {
                    'number': {
                        'description': 'An integer',
                        'type': 'string'
                    }
                },
                'required': []
            }
        }
    }
]


def run(client: OpenAI, model: str, test: str = None):
    messages = []
    messages.append({
        "role": "system",
        "content": base_system_prompt + "\n"
    })

    # TODO: no user message with this tool?
    messages.append({
        "role": "user",
        "content": "What's the myfunction of 3"
    })

    result = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto',
        temperature=0.00000001
    )

    while result.choices[0].finish_reason == "tool_calls":
        messages.append(result.choices[0].message)
        result = process_tool_call(client, result, model, messages, tools)

    print(result.choices[0].message.content)


def process_tool_call(client: OpenAI, response, model: str, messages: list, tools: list):
    for tool in response.choices[0].message.tool_calls:
        if tool.function.name == "myfunction":
            function_response = myfunction(client, model, tool.function.arguments)
            messages.append({
                "role": "tool",
                "name": "myfunction",
                "content": str(function_response.choices[0].message.content),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "sub":
            messages.append({
                "role": "tool",
                "name": "sub",
                "content": sub(tool.function.arguments),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "mul":
            messages.append({
                "role": "tool",
                "name": "mul",
                "content": mult(tool.function.arguments),
                "tool_call_id": tool.id
            })

    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto',
        temperature=0.00000001
    )


def myfunction(client: OpenAI, model: str, args: str):
    args = json.loads(args)

    my_function_tools = [
        {
            'type': 'function',
            'function': {
                'name': 'sub',
                'description': "Subtract two numbers",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'left': {
                            'description': 'a number',
                            'type': 'string'
                        },
                        'right': {
                            'description': 'a number',
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
                'name': 'mul',
                'description': "Multiply two numbers",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'left': {
                            'description': 'a number',
                            'type': 'string'
                        },
                        'right': {
                            'description': 'a number',
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
                'name': 'myfunction',
                'description': "A function taking an integer as argument and returns an integer",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'number': {
                            'description': 'An integer',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": base_system_prompt + """
Do the following in strict order:
1. If ${number} is 0 skip the remaining steps and return 1
2. Calculate the myfunction of (${number} - 1)
3. Return ${number} multiply the result of the previous step

            """
        },
        {
            "role": "user",
            "content": json.dumps({"number": str(args["number"])})
        }
    ]

    result = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=my_function_tools,
        tool_choice='auto',
        temperature=0.00000001
    )

    while result.choices[0].finish_reason == "tool_calls":
        messages.append(result.choices[0].message)
        result = process_tool_call(client, result, model, messages, tools)

    return result


def sub(args: str):
    args = json.loads(args)
    return str(int(args["left"]) - int(args["right"]))


def mult(args: str):
    args = json.loads(args)
    return str(int(args["left"]) * int(args["right"]))
