from typing import List
from code_sushi.context import Context, LogLevel
from code_sushi.core.file import File
from .utils import print_details, get_files_from_folder, filter_out_bad_files

"""
Processor module for Code Sushi.

This module handles the core logic for reading files, parsing code into
functions/classes, and organizing outputs for LLM consumption.
"""

def scan_repo(context: Context) -> List[File]:
    """
    Scan the repository for files to process.
    """
    
    files = get_files_from_folder(context.repo_path)
    files = filter_out_bad_files(context, files)

    # Convert to File objects
    files = [File(context.repo_path, file) for file in files]

    if context.log_level.value >= LogLevel.VERBOSE.value:
        print_details(files)
    
    return files
