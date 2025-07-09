import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes procided content to specified file.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file path to the file to write content to.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content that needs to be written to the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(abs_working_dir, file_path))
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
    try:
        with open(abs_file_path, "w") as file:
            file.write(content)
    except Exception as e:
        return f"Error: {e}"
  
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'