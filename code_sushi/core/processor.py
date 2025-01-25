from typing import List
import os
import pathspec
from pathspec import PathSpec
from code_sushi.context import Context
from code_sushi.core.file import File
import mimetypes

"""
Processor module for Code Sushi.

This module handles the core logic for reading files, parsing code into
functions/classes, and organizing outputs for LLM consumption.
"""

def load_gitignore_patterns(path=".gitignore") -> PathSpec:
    """
    Loads patterns from the .gitignore file to know which files/folders to skip.
    """
    with open(path, "r") as gitignore_file:
        gitignore_patterns = gitignore_file.read()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns.splitlines())

    return spec

def scan_repo(context: Context) -> List[File]:
    """
    Scan the repository for files to process.
    """
    
    # Get the list of files in the repository
    files = []
    for root, _, filenames in os.walk(context.repo_path):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            files.append(path)
    
    # Filter out paths that match regex lines in .gitignore
    gitignore = load_gitignore_patterns(f"{context.repo_path}/.gitignore")
    files = [file for file in files if not gitignore.match_file(file)]
    
    # Ignore all files under .git/ directory
    files = [file for file in files if ".git" not in file.split(os.path.sep)]

    # Filter out non-text files
    def is_code_file(file):
        mime_type, _ = mimetypes.guess_type(file)
        return not mime_type or ((mime_type.startswith("text/") or mime_type.startswith("application/json")))
    
    files = [file for file in files if is_code_file(file)]

    # Convert to File objects
    files = [File(context.repo_path, file) for file in files]
    print_details(files)
    return files

def print_details(files: List[str]):
    """
    Print the details of the files to be processed.
    """
    for file in files:
        print(file)
