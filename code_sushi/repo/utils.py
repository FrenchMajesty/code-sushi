from typing import List, Optional
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
    Get the list of files in the given directory.
    """
    files = []
    for root, _, filenames in os.walk(folder_path):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename))
            files.append(path)

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
