import os
import sys
from typing import Any, Dict, List, cast

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import call_function
from config import get_config

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
gemini = genai.Client(api_key=api_key)

if len(sys.argv) < 2:
    print("Usage: python main.py <prompt>")
    sys.exit(1)

user_prompt = sys.argv[1]

is_verbose = len(sys.argv) > 2 and sys.argv[2] == "--verbose"

if is_verbose:
    print(f"User prompt: {user_prompt}")


def handle_response(
    response: types.GenerateContentResponse, messages: List[types.Content]
) -> tuple[bool, List[types.Content]]:
    function_called = False

    if response.function_calls:
        function_called = True
        # Add the model's response that contains the function calls
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        # Collect all function responses into a single message
        function_response_parts = []
        for function_call in response.function_calls:
            function_call_result = call_function(function_call, verbose=is_verbose)

            # Extract the function response part from the result
            if function_call_result.parts and len(function_call_result.parts) > 0:
                function_response_parts.append(function_call_result.parts[0])

                if is_verbose:
                    part = function_call_result.parts[0]
                    if hasattr(part, "function_response") and part.function_response:
                        response_data: Dict[str, Any] = getattr(
                            part.function_response, "response", {}
                        )
                        print(f"-> {response_data}")

        # Add a single tool message with all function responses
        if function_response_parts:
            messages.append(types.Content(role="tool", parts=function_response_parts))
    else:
        # Only add candidate content if there are no function calls
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)

        if response.text:
            print("Final response:")
            print(response.text)

    if is_verbose and response.usage_metadata:
        prompt_tokens = response.usage_metadata.prompt_token_count
        response_tokens = response.usage_metadata.candidates_token_count

        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")

    return function_called, messages


messages: List[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)])
]

remaining_iterations = 20

while remaining_iterations > 0:
    remaining_iterations -= 1

    response = gemini.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=cast(Any, messages),  # Cast to Any to satisfy type checker
        config=get_config(),
    )

    function_called, messages = handle_response(response, messages)

    if not function_called:
        break
