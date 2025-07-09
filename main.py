import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python import schema_run_python_file
from functions.call_function import call_function

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("prompt", help="User prompt")

args = parser.parse_args()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read content of a file
- Write content to a file
- Run Python file

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls
"""
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)
user_prompt = args.prompt
if not user_prompt.strip():
    print("Error: Empty prompt provided.")
    sys.exit(1)
messages = [
types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(
model="gemini-2.0-flash-001",
contents=messages,
config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt),
)
used_functions = response.function_calls
called = False
if used_functions:
    called = True
    for function_call_part in used_functions:
        function_call_result = call_function(function_call_part, args.verbose)
        if not function_call_result.parts[0].function_response.response:
            raise Exception("Fatal exception of some sort")
        if args.verbose:
            print(f"-> {function_call_result.parts[0].function_response.response}")


if args.verbose:
    print(f"User prompt: {user_prompt}")
    if not called:
        print(response.text)
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
else:
    if not called:
        print(response.text)

