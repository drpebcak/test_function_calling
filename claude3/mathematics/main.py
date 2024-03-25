import os
import sys

import xmltodict

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
import claude3.prompts as prompts

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


def run(client, model: str, test: str = None):
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

    system_prompt = prompts.construct_tool_use_system_prompt(tools) + base_system_prompt

    messages = []
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
    elif test == "chaining":  # This example of chaining can lead to hallucination
        messages.append({
            "role": "user",
            "content": "What is four plus six? What is the result of that plus 2? Take the result and multiply by 5 and then divide by two."
        })

    result = client.messages.create(
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        model=model,
        temperature=0.00000001,
        stop_sequences=["</function_calls>"],
    )

    while result.role == "assistant" and result.stop_reason == "stop_sequence" and result.stop_sequence in [
        "</function_calls>"]:
        messages.append({
            "role": "assistant",
            "content": result.content[0].text + result.stop_sequence
        })
        result = process_tool_calls(
            client=client,
            response=result,
            model=model,
            messages=messages,
            tools=tools
        )

    print(result.content[0].text)


def process_tool_calls(client, response, model: str, messages: list, tools: list):
    system_prompt = prompts.construct_tool_use_system_prompt(tools) + base_system_prompt

    for content in response.content:
        function_calls_xml = content.text + response.stop_sequence
        function_calls_xml = function_calls_xml[function_calls_xml.find("<"):]

        function_calls = xmltodict.parse(function_calls_xml)["function_calls"]["invoke"]
        if type(function_calls) != list:
            function_calls = [function_calls]

        for function_call in function_calls:
            tool_outputs = []
            if function_call["tool_name"] == "addition":
                tool_outputs.append({
                    "tool_name": "addition",
                    "content": add(function_call["parameters"]),
                })
            elif function_call["tool_name"] == "subtraction":
                tool_outputs.append({
                    "tool_name": "subtraction",
                    "content": sub(function_call["parameters"]),
                })
            elif function_call["tool_name"] == "multiplication":
                tool_outputs.append({
                    "tool_name": "multiplication",
                    "content": mult(function_call["parameters"]),
                })
            elif function_call["tool_name"] == "division":
                tool_outputs.append({
                    "tool_name": "division",
                    "content": div(function_call["parameters"]),
                })

            tool_outputs_xml = prompts.construct_tool_outputs_message(tool_outputs, None)
            messages.append({
                "role": "user",
                "content": tool_outputs_xml,
            })
    return client.messages.create(
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        model=model,
        temperature=0.00000001,
        stop_sequences=["</function_calls>"],
    )


def add(args: dict):
    return str(int(args["a"]) + int(args["b"]))


def sub(args: dict):
    return str(int(args["a"]) - int(args["b"]))


def mult(args: dict):
    return str(int(args["a"]) * int(args["b"]))


def div(args: dict):
    return str(int(args["a"]) / int(args["b"]))
