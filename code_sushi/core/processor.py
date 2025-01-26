from typing import List
import os
from code_sushi.context import Context, LogLevel
from .file import File
from code_sushi.vector import VoyageEmbed
from .utils import (
    print_details,
    get_files_from_folder,
    filter_out_bad_files,
    shallow_root_scan,
    get_root_files,
)

"""
Processor module for Code Sushi.

This module handles the core logic for reading files, parsing code into
functions/classes, and organizing outputs for LLM consumption.
"""

def scan_repo(context: Context) -> List[File]:
    """
    Scan the repository for files to process.
    """
    
    # Shallow pass: list content at root level
    dirs = shallow_root_scan(context)
    files = get_root_files(context)

    # Deep pass: list content in subdirectories
    for directory in dirs:
        sub_files = get_files_from_folder(directory)
        files.extend(sub_files)

        if context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"{len(sub_files)} files found in {directory}")
    
    files = filter_out_bad_files(context, files)

    # Convert to File objects
    files = [File(context.repo_path, file) for file in files]

    if context.log_level.value >= LogLevel.VERBOSE.value:
        print_details(files)
    
    return files

def write_summary_to_file(context: Context, file: File, summary: str):
    """
    Store the summary of the file and the file content.
    """
    
    name = file.clean_path

    if ".functions/" in name:
        name = name.replace(".functions/", "@").rsplit('.', 1)[0]

    content = open(file.absolute_path).read()
    template = '\n'.join([
        f"# File: {name}",
        f"## Summary: {summary}",
        "----",
        content
    ])

    # Write to destination
    dest = os.path.join(context.output_dir + file.clean_path)
    if not dest.endswith('.md'):
        dest += '.md'

    if context.log_level.value >= LogLevel.VERBOSE.value:
        print(f"Writing {len(template)} chars to {dest}")

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    try:
        with open(dest, 'w') as f:
            f.write(template)
    except Exception as e:
        print(f"Error writing to file: {e}")

def embed_the_summaries(context: Context):
    """
    Parses the summaries for every file and chunk written to disk to vectorize them.
    """

    """
    - Read all the files in context.output_dir
    - For each file, read the content and extract the metadata (from start to first '----')
    The format of the heading is this:
    # File: <filename>
    ## Summary: <summary>
    .
    - We extract both the filename and the summary
    - We vectorize the summary text using Voyage
    - We store and upload it to the vector DB

    """
