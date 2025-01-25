from together import Together
from dotenv import load_dotenv
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
def summarize_file(file_path: str, content: str):
    """
    Summarize the provided file using an LLM.

    Args:
        file_path (str): Path to the file being summarized.
        content (str): Full content of the file.

    Returns:
        str: LLM-generated summary.
    """
    pass

    completion = client.chat.completions.create(
    model=model,
    messages= list(summarize_file_prompt).extend[
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

    print(completion)
    return completion.choices[0].message.content
