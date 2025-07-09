import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory, directory=None):
    abs_working_dir = os.path.abspath(working_directory)

    # If directory is None, we assume the working directory itself
    if directory is None:
        abs_target_dir = abs_working_dir
    else:
        # Interpret directory as relative to working_directory
        abs_target_dir = os.path.abspath(os.path.join(abs_working_dir, directory))

    # Guardrail 1: prevent escaping working directory
    if not abs_target_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    # Guardrail 2: ensure it's a real directory
    if not os.path.isdir(abs_target_dir):
        return f'Error: "{directory}" is not a directory'

    try:
        content = os.listdir(abs_target_dir)
    except (FileNotFoundError, PermissionError, NotADirectoryError, OSError) as e:
        return f"Error: {e}"

    result = ""
    for element in content:
        path = os.path.join(abs_target_dir, element)

        try:
            size = os.path.getsize(path)
        except (FileNotFoundError, PermissionError, OSError) as e:
            size = f"Error: {e}"

        try:
            is_dir = os.path.isdir(path)
        except (FileNotFoundError, PermissionError, OSError) as e:
            is_dir = f"Error: {e}"

        result += f"- {element}: file_size={size} bytes, is_dir={is_dir}\n"

    return result

