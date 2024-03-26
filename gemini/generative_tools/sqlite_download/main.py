import json
import os
import sys

import xmltodict

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
import claude3.prompts as prompts

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
from tools import main as sysstuff

systools = sysstuff.tools

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions. Be as succinct as possible.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


def run(client, model: str, test: str = None):
    tools = [
        systools["sys.download"],
        systools["sys.exec"],
        systools["sys.remove"]
    ]

    system_prompt = prompts.construct_tool_use_system_prompt(tools) + base_system_prompt

    messages = []
    messages.append({
        "role": "user",
        "content": """
Download https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip to a
random file. Then expand the archive to a temporary location as there is a sqlite
database in it.

<scratchpad>Use sqlite commands that will exit on their own, without interaction.</scratchpad>
First inspect the schema of the database to understand the table structure.

Form and run a SQL query to find the artist with the most number of albums and output
the result of that.

When done remove the database file and the downloaded content.
"""
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

        tool_outputs = []
        for function_call in function_calls:
            if function_call["tool_name"] == "sys-download":
                tool_outputs.append({
                    "tool_name": "sys-downloaad",
                    "content": str(sysstuff.sys_download(json.dumps(function_call["parameters"]))),
                })
            elif function_call["tool_name"] == "sys-exec":
                tool_outputs.append({
                    "tool_name": "sys-exec",
                    "content": str(sysstuff.sys_exec(json.dumps(function_call["parameters"]))),
                })
            elif function_call["tool_name"] == "sys-remove":
                tool_outputs.append({
                    "tool_name": "sys-remove",
                    "content": str(sysstuff.sys_remove(json.dumps(function_call["parameters"]))),
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
