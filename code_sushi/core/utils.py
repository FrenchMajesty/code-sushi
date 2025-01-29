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

def shallow_root_scan(context: Context) -> List[str]:
    """
    Shallow scan the root of repository for directories to process while ignoring bad directories.
    """
    dirs = [d for d in os.listdir(context.repo_path) if os.path.isdir(os.path.join(context.repo_path, d))]
    dirs = filter_out_bad_dirs(context, dirs)

    dirs = [os.path.abspath(os.path.join(context.repo_path, d)) for d in dirs]

    return dirs

def get_root_files(context: Context) -> List[str]:
    """
    Get the root files in the repository.
    """
    files = [
        os.path.abspath(os.path.join(context.repo_path, f))
        for f in os.listdir(context.repo_path)
        if os.path.isfile(os.path.join(context.repo_path, f))
    ]
    
    return files

def get_files_from_folder(folder_path: str) -> List[str]:
    """
    Get the list of files in the given directory.
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

    if context.log_level.value >= LogLevel.VERBOSE.value:
        print(f"Found {name} file? {found}")
    
    return spec

def filter_out_bad_dirs(context: Context, dirs: List[str]) -> List[str]:
    """
    Filter out the directories that are not useful or desirable for processing.
    """
    show_debug = context.log_level.value >= LogLevel.DEBUG.value

    if show_debug:
        print(f"\n--> Filtering out bad directories. Starting at {len(dirs)}")

    # Filter out paths that match regex lines in .gitignore
    gitignore = load_ignore_patterns(context, ".gitignore")
    if gitignore:
        dirs = [dir for dir in dirs if not gitignore.match_file(dir + '/')]

        if show_debug:
            print(f"After .gitignore: {len(dirs)}")

    # Use .sushiignore to filter out directories
    sushiignore = load_ignore_patterns(context, ".sushiignore")
    if sushiignore:
        dirs = [dir for dir in dirs if not sushiignore.match_file(dir + '/')]

        if show_debug:
            print(f"After .sushiignore: {len(dirs)}")

    # Ignore content in .git/ directory
    dirs = [dir for dir in dirs if dir != ".git"]

    # Ignore content in .llm/ directory
    dirs = [dir for dir in dirs if dir != ".llm"]

    if show_debug:
        print(f"Final dirs count: {len(dirs)}")

    return dirs

def filter_out_bad_files(context: Context, files: List[str]) -> List[str]:
    """
    Filter out the files that are not useful or desirable for processing.
    """
    show_debug = context.log_level.value >= LogLevel.DEBUG.value

    if show_debug:
        print(f"\n --> Filtering out bad files. Starting at {len(files)}")

    # Filter out files that match regex lines in .gitignore
    gitignore = load_ignore_patterns(context, ".gitignore")
    if gitignore:
        files = list(gitignore.match_files(files, negate=True))

        if show_debug:
            print(f"After .gitignore: {len(files)}")

    # Use .sushiignore to filter out files
    sushiignore = load_ignore_patterns(context, ".sushiignore")
    if sushiignore:
        files = list(sushiignore.match_files(files, negate=True))

        if show_debug:
            print(f"After .sushiignore: {len(files)}")
    
    files = [file for file in files if is_code_file(file)]
    if show_debug:
        print(f"After file extension check: {len(files)}")

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

    # Sort the file types by line count before printing
    file_type_distribution = dict(sorted(file_type_distribution.items(), key=lambda item: item[1], reverse=True))
    
    if printing:
        print("\n-- File Extension Distribution:\n")
    insights.append("File Extension Distribution:")
    for file_type, line_count in file_type_distribution.items():
        type = file_type if file_type else "?"
        insight = f"{type}:\t {line_count:,} lines"
        total_lines += line_count
        if printing:
            print(insight)
        insights.append(insight)

    if printing:
        print(f"\nTotal lines of code: {total_lines:,}")
    insights.append(f"Total lines of code: {total_lines:,}")    

    return insights

def extract_metadata_from_output_file(file: str) -> Optional[dict]:
    """
    Extract metadata from a file which has already been through LLM summarization.
    """
    metadata = {}

    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('----'):
                    break
                if line.startswith('# File:'):
                    metadata['file'] = line.split(':', 1)[1].strip()
                elif line.startswith('## Summary:'):
                    metadata['summary'] = line.split(':', 1)[1].strip()
        
        return metadata
    except Exception as e:
        print(f"Error extracting metadata from file: {e}")
        return None
