import os
import sys
from typing import Dict, Any, Sequence, cast

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt
from tools import (
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
)
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

if len(sys.argv) < 2:
    print("Usage: python main.py <prompt>")
    sys.exit(1)

user_prompt = sys.argv[1]

is_verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

if is_verbose:
    print(f"User prompt: {user_prompt}")

messages: Sequence[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False) -> types.Content:
    function_name = function_call_part.name

    if verbose:
        print(f"Calling function: {function_name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Add working_directory to the args
    args = dict(function_call_part.args)
    args["working_directory"] = "./calculator"

    try:
        function_result = function_map[function_name](**args)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": str(e)},
                )
            ],
        )


response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[available_functions],
    ),
)
if response.function_calls:
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose=is_verbose)

        if is_verbose and function_call_result.parts:
            # The first part should be a function response created by Part.from_function_response
            part = function_call_result.parts[0]
            if hasattr(part, "function_response") and part.function_response:
                response_data: Dict[str, Any] = getattr(
                    part.function_response, "response", {}
                )
                print(f"-> {response_data}")
else:
    print(response.text)

if is_verbose and response.usage_metadata:
    prompt_tokens = response.usage_metadata.prompt_token_count
    response_tokens = response.usage_metadata.candidates_token_count

    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")
