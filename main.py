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
for _ in range(20):
    try:    
        response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(tools=[available_functions],system_instruction=system_prompt),
        )
        for candidate in response.candidates:
            messages.append(candidate.content)
        used_functions = response.function_calls
    
        if used_functions:
            for function_call_part in used_functions:
                function_call_result = call_function(function_call_part, args.verbose)
                response_dict = function_call_result.parts[0].function_response.response
                messages.append(function_call_result)
                if 'error' in response_dict:
                    print(f"Error calling function: {response_dict['error']}")
                    break
                if args.verbose:
                    print(f"-> {response_dict}")
        else:
            print("Final response:")
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text"):
                        print(part.text)
            break
    except Exception as e:
        print(f"Error: {e}")
        break

if args.verbose:
    print(f"User prompt: {user_prompt}")
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


