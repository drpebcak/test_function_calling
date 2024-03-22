import json

from openai import OpenAI

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
"""


def run(client: OpenAI, model: str):
    messages = []
    messages.append({
        "role": "system",
        "content": base_system_prompt + "\nAsk Bob how he is doing and let me know exactly what he said."
    })

    messages.append({
        "role": "user",
        "content": "--question=How are you?"
    })

    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'chaining',
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

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto'
    )

    if response.choices[0].finish_reason == "tool_calls":
        messages.append(response.choices[0].message)

        if response.choices[0].message.tool_calls[0].function.name == "chaining":
            function_response = chaining(client, model, response.choices[0].message.tool_calls[0].function.arguments)
            messages.append({
                "role": "tool",
                "name": "chaining",
                "content": function_response.choices[0].message.content,
                "tool_call_id": response.choices[0].message.tool_calls[0].id
            })

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice='auto'
        )

    print(response.choices[0].message.content)


def chaining(client: OpenAI, model: str, args: str):
    args = json.loads(args)
    messages = [
        {
            "role": "system",
            "content": base_system_prompt + "\nWhen asked how I am doing, respond with \"Thanks for asking \"${question}\", I'm doing great fellow friendly AI tool!\""
        },
        {
            "role": "user",
            "content": f"--question={args['question']}"
        }
    ]
    result = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return result
