import subprocess
from pathlib import Path


def run_python_file(working_directory: str, file_path: str):
    working_dir = Path(working_directory).resolve()
    target_file_path = (Path(working_directory) / file_path).resolve()

    if not target_file_path.is_relative_to(working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not target_file_path.exists():
        return f'Error: File "{file_path}" not found.'

    if not target_file_path.is_file():
        return f'Error: File "{file_path}" is not a file.'

    if not target_file_path.suffix == ".py":
        return f'Error: "{file_path}" is not a Python file.'

    try:
        result = subprocess.run(
            ["python", str(file_path)],
            check=True,
            timeout=30,
            capture_output=True,
            cwd=working_directory,
        )

        stdout = result.stdout.decode("utf-8")
        stderr = result.stderr.decode("utf-8")

        output = f"Succefully ran '{file_path}'\n"
        output += f"STDOUT:{stdout}\n" if stdout else "No output produced."

        if stderr:
            output += f"STDERR:{stderr}\n"

        if result.returncode != 0:
            output += f"Process exited with code {result.returncode}\n"

        return output

    except subprocess.CalledProcessError as e:
        return f"Error: executing Python file: {e}"
