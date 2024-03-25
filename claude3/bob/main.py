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


def run(client, model):
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'bob',
                'description': "I'm Bob, a friendly guy.",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'question': {
                            'description': 'The question to ask Bob.',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        }
    ]

    system_prompt = prompts.construct_tool_use_system_prompt(tools)
    system_prompt += "\nAsk Bob how he is doing and let me know exactly what he said."

    messages = []
    messages.append({
        "role": "user",
        "content": "--question=How are you?"
    })

    response = client.messages.create(
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        model=model,
        temperature=0.00000001,
        stop_sequences=["</function_calls>"],
    )

    if response.role == "assistant" and response.stop_reason == "stop_sequence" and response.stop_sequence in [
        "</function_calls>"]:
        for content in response.content:
            function_calls_xml = content.text + response.stop_sequence
            messages.append({
                "role": "assistant",
                "content": function_calls_xml,

            })
            function_calls = xmltodict.parse(function_calls_xml)["function_calls"]["invoke"]
            if type(function_calls) != list:
                function_calls = [function_calls]

            for function_call in function_calls:
                if function_call["tool_name"] == "bob":
                    response = bob(client, model, function_call["parameters"])
                    tool_outputs = [{
                        "tool_name": "bob",
                        "content": response.content[0].text,
                    }]
                    tool_outputs_xml = prompts.construct_tool_outputs_message(tool_outputs, None)
                    messages.append({
                        "role": "user",
                        "content": tool_outputs_xml,
                    })

        response = client.messages.create(
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            model=model,
            temperature=0.00000001,
            stop_sequences=["</function_calls>"],
        )
    print(response.content[0].text)


def bob(client, model, parameters):
    system_prompt = "\nWhen asked how I am doing, respond with \"Thanks for asking \"${question}\", I'm doing great fellow friendly AI tool!\""
    messages = [
        {
            "role": "user",
            "content": f"--question={parameters['question']}"
        }
    ]
    return client.messages.create(
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        model=model,
        temperature=0.00000001,
        # stop_sequences=["</function_calls>"],
    )
