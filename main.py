import os
import sys
from typing import Dict, Any, Sequence

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import get_config

from call_function import call_function

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


response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=get_config(),
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
