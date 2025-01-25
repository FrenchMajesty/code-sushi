from typing import List
from code_sushi.core.file import File
import os
import mimetypes
from code_sushi.context import Context, LogLevel
import pathspec
from pathspec import PathSpec

def print_details(files: List[File]):
    """
    Print the details of the files to be processed.
    """
    for file in files:
        print(file)

def get_files_from_folder(folder_path: str) -> List[str]:
    """
    Get the list of files in the repository.
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            files.append(path)
    return files

def load_gitignore_patterns(context: Context) -> PathSpec:
    """
    Loads patterns from the .gitignore file to know which files/folders to skip.
    """
    path = f"{context.repo_path}/.gitignore"
    found = False
    with open(path, "r") as gitignore_file:
        found = True
        gitignore_patterns = gitignore_file.read()
    spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns.splitlines())

    if context.log_level.value >= LogLevel.DEBUG.value:
        print(f"Found .gitignore file? {found}")
    
    return spec

def filter_out_bad_files(context: Context, files: List[str]) -> List[str]:
    """
    Filter out the files that are not useful or desirable for processing.
    """
    # Filter out paths that match regex lines in .gitignore
    gitignore = load_gitignore_patterns(context)
    files = [file for file in files if not gitignore.match_file(file)]
    
    # Ignore all files under .git/ directory
    files = [file for file in files if ".git" not in file.split(os.path.sep)]

    # Filter out non-text files
    def is_code_file(file):
        mime_type, _ = mimetypes.guess_type(file)
        return not mime_type or ((mime_type.startswith("text/") or mime_type.startswith("application/json")))
    
    files = [file for file in files if is_code_file(file)]

    return files
