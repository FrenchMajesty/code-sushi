from typing import List, Optional
from code_sushi.core.file import File
import os
import mimetypes
from code_sushi.context import Context, LogLevel
import pathspec
from pathspec import PathSpec
from .code_file_filter import is_code_file

def print_details(files: List[File]):
    """
    Print the details of the files to be processed.
    """
    for file in files:
        print(file)

def get_files_from_folder(folder_path: str) -> List[File]:
    """
    Get the list of files in the repository.
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            files.append(path)

    return files

def load_ignore_patterns(context: Context, name: str) -> Optional[PathSpec]:
    """
    Loads patterns from a .gitignore-type file to know which files/folders to skip.
    """
    path = '/'.join([context.repo_path, name])
    found = False
    try:
        with open(path, "r") as gitignore_file:
            found = True
            gitignore_patterns = gitignore_file.read()
        spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns.splitlines())
    except FileNotFoundError:
        spec = None

    if context.log_level.value >= LogLevel.DEBUG.value:
        print(f"Found {name} file? {found}")
    
    return spec

def filter_out_bad_files(context: Context, files: List[str]) -> List[str]:
    """
    Filter out the files that are not useful or desirable for processing.
    """
    show_debug = context.log_level.value >= LogLevel.DEBUG.value

    if show_debug:
        print(f"Filtering out bad files. Starting at {len(files)}")

    # Filter out paths that match regex lines in .gitignore
    gitignore = load_ignore_patterns(context, ".gitignore")
    if gitignore:
        files = [file for file in files if not gitignore.match_file(file)]

        if show_debug:
            print(f"Files after .gitignore: {len(files)}")

    #    exit(1)
    sushiignore = load_ignore_patterns(context, ".sushiignore")
    if sushiignore:
        files = [file for file in files if not sushiignore.match_file(file)]

        if show_debug:
            print(f"Files after .sushiignore: {len(files)}")
    
    # Ignore all files under .git/ directory
    files = [file for file in files if ".git" not in file.split(os.path.sep)]

    if show_debug:
        print(f"Files after .git: {len(files)}")
    
    files = [file for file in files if is_code_file(file)]
    if show_debug:
        print(f"Files after code-file check: {len(files)}")

    return files

  
def get_code_insights(files: List[File], printing: bool = False) -> List[str]:
    """
    Get code insights from the files. Figure out the distribution of file types in terms of lines of code
    and which folders have the most code.
    """
    insights = []
    file_type_distribution = {}
    total_lines = 0

    for file in files:
        file_extension = os.path.splitext(file.absolute_path)[1]
        if file_extension not in file_type_distribution:
            file_type_distribution[file_extension] = 0
        file_type_distribution[file_extension] += file.line_count

    if printing:
        print("\n-- File Extension Distribution:\n")
    insights.append("File Extension Distribution:")
    for file_type, line_count in file_type_distribution.items():
        type = file_type if file_type else "?"
        insight = f"{type}: {line_count:,} lines"
        total_lines += line_count
        if printing:
            print(insight)
        insights.append(insight)

    if printing:
        print(f"\nTotal lines of code: {total_lines:,}")
    insights.append(f"Total lines of code: {total_lines:,}")    

    return insights
