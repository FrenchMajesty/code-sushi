from langchain.schema import SystemMessage, HumanMessage, AIMessage

summarize_file_prompt = [
    {
        "role": "system",
        "content": "You are an expert software engineer. Your task is to summarize what the provided file does in a couple sentences."
    },
    {
        "role": "user",
        "content": """
# path: code_sushi/context.py
---
from typing import Optional
from enum import Enum

class LogLevel(Enum):
    NONE = 0
    INFO = 1
    DEBUG = 2
    VERBOSE = 3


class Context:
    def __init__(self, repo_path: Optional[str] = None, log_level: int = 1):
        self.repo_language: Optional[str] = None
        self.repo_path: Optional[str] = repo_path
        self.log_level: LogLevel = LogLevel(log_level)
        """
    },
    {
        "role": "system",
        "content": "This file defines an enumeration LogLevel with four levels of logging (NONE, INFO, DEBUG, VERBOSE) and a Context class that initializes a context object with a repository path and log level. The Context class is designed to store information about a repository, including its path, language, and logging level."
    },
    {
        "role": "user",
        "content": '''
        # path: code_sushi/repo/repo_scanner.py
        # Parent File Summary: code_sushi/repo/repo_scanner.py
        ---
        def get_root_files(self) -> List[str]:
        """
        Get the root files in the repository.
        """
        files = [
            os.path.abspath(os.path.join(self.context.repo_path, f))
            for f in os.listdir(self.context.repo_path)
            if os.path.isfile(os.path.join(self.context.repo_path, f))
        ]
        
        return files
        '''
    },
    {
        "role": "system",
        "content": "The get_root_files() method in repo_scanner.py retrieves the absolute file paths of all files (excluding directories) located directly in the repository's root directory by listing entries, filtering for files, and converting their paths to absolute formats.",
    }
]

question_chat_prompt = [
    {
        "role": "system",
        "content": "You are an expert software engineer. Your task is to answer the user's questions about their project by using the provided context or your understanding of the language and frameworks involved if necessary."
    },
    {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
    }
]
