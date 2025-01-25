from typing import List
import os
from code_sushi.context import Context, LogLevel
from .file import File
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

def write_summary(context: Context, file: File, summary: str):
    """
    Store the summary of the file and the file content.
    """

    content = open(file.absolute_path).read()
    template = f"""
    # File: {file.clean_path}
    ## Summary: {summary}
    ----
    {content}
    """

    # Write to destination
    dest = os.path.join(context.output_dir, file.file_name + '.md')
    with open(dest, 'w') as f:
        f.write(template)
    