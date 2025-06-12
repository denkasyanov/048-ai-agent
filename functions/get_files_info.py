from pathlib import Path


def get_files_info(working_directory, directory=None):
    # We like to work with pathlib.Path
    working_directory = Path(working_directory).resolve()

    if directory is not None:
        target_directory = (working_directory / directory).resolve()
    else:
        target_directory = working_directory

    if not target_directory.is_relative_to(working_directory):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not target_directory.exists():
        return f'Error: "{directory}" does not exist'

    if not target_directory.is_dir():
        return f'Error: "{directory}" is not a directory'

    # Build and return a string representing the contents of the directory
    try:
        result_lines = []
        for item in sorted(target_directory.iterdir()):
            size = item.stat().st_size
            line = f"- {item.name}: file_size={size} bytes, is_dir={item.is_dir()}"
            result_lines.append(line)
        return "\n".join(result_lines)

    except Exception as e:
        return f"Error: Failed to list directory contents: {str(e)}"
