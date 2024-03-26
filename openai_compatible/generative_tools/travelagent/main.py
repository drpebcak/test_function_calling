import json
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
Plan a vacation in France starting on March 1 for two weeks
"""
    })

    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'travelagent',
                'description': "Plans a vacation",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'destination': {
                            'description': 'Destination to plan the vacation for',
                            'type': 'string'
                        },
                        'start': {
                            'description': 'Date to start the vacation on',
                            'type': 'string'
                        },
                        'end': {
                            'description': 'Date to end the vacation on',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        },
    ]

    result = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto'
    )

    while result.choices[0].finish_reason == "tool_calls":
        messages.append(result.choices[0].message)
        print("MESSAGES: ", messages)
        result = process_tool_call(client, result, model, messages, tools)

    # completed
    print(result.choices[0].message.content)


def process_tool_call(client: OpenAI, response, model: str, messages: list, tools: list):
    for tool in response.choices[0].message.tool_calls:
        if tool.function.name == "sys-write":
            messages.append({
                "role": "tool",
                "name": "sys-write",
                "content": str(sysstuff.sys_write(tool.function.arguments)),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "travelagent":
            messages.append({
                "role": "tool",
                "name": "travelagent",
                "content": str(travelagent(client, model, tool.function.arguments)),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "search":
            messages.append({
                "role": "tool",
                "name": "search",
                "content": str(search(client, model, tool.function.arguments)),
                "tool_call_id": tool.id
            })
        elif tool.function.name == "sys-http-html2text":
            messages.append({
                "role": "tool",
                "name": "sys-http-html2text",
                "content": str(sysstuff.sys_http_html2text(tool.function.arguments)),
                "tool_call_id": tool.id
            })

    return client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice='auto',
        temperature=0.00000001
    )


def travelagent(client, model, args):
    system_prompt = base_system_prompt + """
You are a very experienced travel agent with a focus on affordable vacations for your clients.

Before starting your job, do a quick search (just one search call) to refresh your knowledge on
what it means to be a travel agent. Use this context to guide how you evaluate the following steps.

Based on the input, do the following in order:
1. Search the web for typical vacation routes in the $destination.
2. Based on the results build an initial outline of locations to include.
3. For each location you determine, search for essential things to do in that location (maximum of one search per location). Include at
   least 5 activities per day and 20 per location.
4. With all of the activities and locations, build out an itinerary that outlines each day and each hour in that day for the trip.
5. Reevaluate the plan and move dates around such that it is optimized for efficient travel
6. Look over the entire thing one more time and ask yourself if its missing anything. If it is, make your edits now.
7. Write all of this into a vacation.md document.
"""
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'search',
                'description': "Searches the internet for content",
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'query': {
                            'description': 'The query to search for',
                            'type': 'string'
                        }
                    },
                    'required': []
                }
            }
        },
        systools["sys.write"]
    ]
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": args
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
        print("MESSAGES: ", messages)
        result = process_tool_call(client, result, model, messages, tools)

    return result.choices[0].message.content


def search(client, model, args):
    system_prompt = base_system_prompt + """
First download the content of "https://www.google.com/q=${encoded_query}".
Look for the first 3 search results. Download each search result and look for content
that would best answer the query ${query}.

With all that information try your best to provide an answer or useful context to ${query}.

If you can not retrieve a referenced URL then just skip that item and make a reference that
that URL was skipped.
    """
    tools = [
        systools["sys.http.html2text"]
    ]
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": args
        }
    ]
    result = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools
    )

    while result.choices[0].finish_reason == "tool_calls":
        messages.append(result.choices[0].message)
        print("MESSAGES: ", messages)
        result = process_tool_call(client, result, model, messages, tools)

    return result.choices[0].message.content
