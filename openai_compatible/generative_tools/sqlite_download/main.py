import os
import sys

from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))

from tools import main as sysstuff

systools = sysstuff.tools

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


def run(client: OpenAI, model: str):
    messages = []
    messages.append({
        "role": "system",
        "content": base_system_prompt
    })

    messages.append({
        "role": "user",
        "content": """
Download https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip to a
random file. Then expand the archive to a temporary location as there is a sqlite
database in it.

First inspect the schema of the database to understand the table structure.

Form and run a SQL query to find the artist with the most number of albums and output
the result of that.

When done remove the database file and the downloaded content.
"""
    })

    tools = [
        systools["sys.download"],
        systools["sys.exec"],
        systools["sys.remove"]
    ]

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

    # completed
    print(result.choices[0].message.content)


def process_tool_call(client: OpenAI, response, model: str, messages: list, tools: list):
    for tool in response.choices[0].message.tool_calls:
        if tool.function.name == "sys-download":
            messages.append({
                "role": "tool",
                "name": "sys-download",
                "content": str(sysstuff.sys_download(tool.function.arguments)),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "sys-exec":
            messages.append({
                "role": "tool",
                "name": "sys-exec",
                "content": str(sysstuff.sys_exec(tool.function.arguments)),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "sys-remove":
            messages.append({
                "role": "tool",
                "name": "sys-remove",
                "content": str(sysstuff.sys_remove(tool.function.arguments)),
                "tool_call_id": tool.id
            })

    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto',
        temperature=0.00000001
    )
