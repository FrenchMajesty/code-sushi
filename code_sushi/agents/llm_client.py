from together import Together
from dotenv import load_dotenv
from code_sushi.context import Context, LogLevel
from typing import Optional
from langchain_together import ChatTogether
from langchain.schema import HumanMessage
from .prompt_guidance import (
    summarize_file_prompt,
    format_for_rag_prompt
)
import time

load_dotenv()

"""
LLM Client for Code Sushi.

This module provides functions to interact with the LLM API, including
making requests and processing responses. Implement API-specific logic here.
"""
client = Together()
primary_model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
small_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"

def summarize_file(context: Context, file_path: str, content: str, file_summary: Optional[str] = None) -> Optional[str]:
    """
    Summarize the provided file using an LLM.
    """
    try:
        if ".functions/" in file_path:
            file_path = file_path.replace(".functions/", "@").rsplit('.', 1)[0]

        if context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Sending req to LLM: {file_path}")

        msg_parts = [
            f"# Path: {file_path}",
            f"## Parent File Summary: {file_summary}" if file_summary else "",
            "--",
            content
        ]
        msg_parts = [part for part in msg_parts if part]

        completion = client.chat.completions.create(
        model=primary_model,
        messages= list(summarize_file_prompt) + [{
                "role": "user", 
                "content": '\n'.join(msg_parts)
            }],
        )

        if context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Received response from LLM", completion.created)

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error in llm_client.summarize_file(): {e}. File: {file_path}")
        return None
    

def format_query_for_rag(context: Context, query: str) -> str:
    """
    Use LLM to re-format the user query for better RAG hits, if necessary.
    """
    try:
        start = time.time()
        if context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Sending req to LLM: {query}")

        llm = ChatTogether(model=small_model)
        request = list(format_for_rag_prompt) + [HumanMessage(query)]
        response = llm.invoke(request)

        if context.log_level.value >= LogLevel.DEBUG.value:
            runtime = time.time() - start
            print(f"Received response from LLM in {runtime:.2f} seconds", response.id)

        return response.content
    except Exception as e:
        print(f"Error in llm_client.format_query_for_rag(): {e}")
        return query
