from pathlib import Path

MAX_CHARS = 10_000


def get_file_content(working_directory, file_path):
    file_path = Path(working_directory) / file_path

    try:
        if not file_path.is_relative_to(working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not file_path.exists() or not file_path.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(file_path, "r") as f:
            content = f.read(
                MAX_CHARS + 1
            )  # Read one extra char to check if truncation needed

        if len(content) > MAX_CHARS:
            return (
                content[:MAX_CHARS]
                + f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            )

        return content
    except Exception as e:
        return f'Error: Failed to read file "{file_path}": {str(e)}'
