import json
import os
import sys

from vertexai.generative_models import (Content, FunctionDeclaration, GenerationConfig, GenerativeModel,
                                        Part, Tool)

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

base_system_prompt = """
You are task oriented system.
You receive input from a user, process the input from the given instructions, and then output the result.
Your objective is to provide consistent and correct results.
You do not need to explain the steps taken, only provide the result to the given instructions.
You are referred to as a tool.
You don't move to the next step until you have a result.
"""


def run(model):
    model = GenerativeModel(model)

    tools = [
        Tool(
            function_declarations=[
                FunctionDeclaration(
                    name="bob",
                    description="I'm Bob, a friendly guy.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "question": {
                                "description": "The question to ask Bob.",
                                "type": "string"
                            }
                        },
                        "required": []
                    }
                )
            ]
        )
    ]

    messages: list[Content] = []
    message = Content(
        role="user",
        parts=[
            Part.from_text(base_system_prompt),
            Part.from_text("Ask Bob how he is doing and let me know exactly what he said."),
            Part.from_text("--question=How are you?")
        ]
    )
    messages.append(message)

    response = model.generate_content(contents=messages,
                                      tools=tools,
                                      generation_config=GenerationConfig(
                                          temperature=0.00000001,
                                          max_output_tokens=4096,
                                      ),
                                      )

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if candidate.content.role == "model" and part.function_call.name != "":
                if part.function_call.name == "bob":
                    response = bob(model, json.dumps(dict(part.function_call.args)))

    print(response)


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
        temperature=0.00000001
    )


run("gemini-pro")
