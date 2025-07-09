import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs python file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file.",
            ),
        },
    ),
)

def run_python_file(working_directory, file_path):
    abs_dir = os.path.abspath(working_directory)
    abs_file = os.path.abspath(os.path.join(abs_dir, file_path))

    if not os.path.commonpath([abs_dir, abs_file]) == abs_dir:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(abs_file):
        return f'Error: File "{file_path}" not found.'
    if not str(abs_file).endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'
    try:
        result = subprocess.run(['python', file_path], capture_output=True, text=True, timeout=30, cwd=working_directory)
    except Exception as e:
        return f'Error: executing Python file: {e}'
    exic_code = result.returncode
    if not result.stdout and not result.stderr:
        return 'No output produced.'
    return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}\n{f'Process exited with code {exic_code}' if exic_code != 0 else ''}"
