from pathlib import Path


def write_file(working_directory, file_path, content):
    file_path = Path(working_directory) / file_path
    if not file_path.is_relative_to(working_directory):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        # Make sure parent directories exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            f.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f'Error: Failed to write to file "{file_path}": {str(e)}'
