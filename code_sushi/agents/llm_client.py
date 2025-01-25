from together import Together
from dotenv import load_dotenv
from code_sushi.context import Context, LogLevel
import os
from .prompt_guidance import (
    summarize_file_prompt
)

load_dotenv()

"""
LLM Client for Code Sushi.

This module provides functions to interact with the LLM API, including
making requests and processing responses. Implement API-specific logic here.
"""
client = Together()
model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Example: Placeholder function
def summarize_file(context: Context, file_path: str, content: str):
    """
    Summarize the provided file using an LLM.
    """

    if context.log_level.value >= LogLevel.DEBUG.value:
        print(f"Sending req to LLM: {file_path}")

    try:
        completion = client.chat.completions.create(
        model=model,
        messages= list(summarize_file_prompt) + [
            {
                "role": "user", 
                "content": f"""
                path: {file_path}
                --
                {content}
                """
                }
            ],
        )
    except Exception as e:
        print(f"Error: {e}")
        return None

    return completion.choices[0].message.content
