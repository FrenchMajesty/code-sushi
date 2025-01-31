from typing import List
import os
from concurrent.futures import ThreadPoolExecutor
from code_sushi.context import Context, LogLevel
from .file import File
import math
from datetime import datetime, timezone

def write_summary_to_file(context: Context, file: File, summary: str):
    """
    Store the summary of the file and the file content.
    """
    try:
        name = file.relative_path

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
        dest = os.path.join(context.output_dir, file.relative_path)
        if not dest.endswith('.md'):
            dest += '.md'

        if context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"Writing {len(template)} chars to {dest}")

        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'w') as f:
            f.write(template)
    except Exception as e:
        print(f"Error writing to file: {e}")
