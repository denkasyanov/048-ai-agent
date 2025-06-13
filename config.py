from google.genai import types

from prompts import system_prompt
from tools import (
    schema_get_file_content,
    schema_get_files_info,
    schema_run_python_file,
    schema_write_file,
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


def get_config():
    return types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[available_functions],
    )
