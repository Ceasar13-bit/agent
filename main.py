import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parser.add_argument("prompt", help="User prompt")

args = parser.parse_args()

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

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
)
if args.verbose:
    print(f"User prompt: {user_prompt}")
    print(response.text)
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
else:
    print(response.text)

