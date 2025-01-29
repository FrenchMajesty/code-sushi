from typing import List
import os
from concurrent.futures import ThreadPoolExecutor
from code_sushi.context import Context, LogLevel
from .file import File
import math
from code_sushi.vector import Voyage, VectorRecord, Pinecone
from datetime import datetime, timezone
from .utils import (
    print_details,
    get_files_from_folder,
    filter_out_bad_files,
    shallow_root_scan,
    get_root_files,
    extract_metadata_from_output_file
)

background_executor = ThreadPoolExecutor()

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

def embed_and_upload_the_summaries(context: Context):
    """
    Parses the summaries for every file and chunk written to disk to vectorize them.
    """
    voyage = Voyage(context)
    vector_db = Pinecone(context)
    files = context.get_files_in_output_dir()

    if context.log_level.value >= LogLevel.INFO.value:
        print(f"Preparing to embed {len(files)} files...")

    chunk_size = 128
    chunk_idx = 0
    total_chunks = math.ceil(len(files) / chunk_size)
    for i in range(0, len(files), chunk_size):
        chunk_idx += 1
        chunk = files[i:i + chunk_size]
        
        if context.log_level.value >= LogLevel.INFO.value:
            print(f"Processing chunk {chunk_idx} of {total_chunks}")

        entries = convert_files_to_vector_records(context, chunk)

        # Mass-embed the text from the entries
        raw_contents = [entry.text for entry in entries]

        if context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"Send req. to embed {len(raw_contents)} text sections")

        embeddings = voyage.embed(raw_contents)
        
        if context.log_level.value >= LogLevel.VERBOSE.value:
            print(f"Received {len(embeddings)} embeddings back")

        if len(embeddings) != len(entries):
            print(f"Error: Embeddings length {len(embeddings)} does not match entries length {len(entries)}")
            continue
        
        # Assign the embeddings to the linked entries
        for i in range(len(entries)):
            entries[i].embedding = embeddings[i]

        # Upload to vector DB
        vector_db.write_many(entries)

def convert_files_to_vector_records(context: Context, files: List[str]) -> List[VectorRecord]:
    """
    Parse the files into partial vector records.
    """
    entries = []
    for i, file_path in enumerate(files):
        try:
            file_meta = extract_metadata_from_output_file(file_path)
            if not file_meta:
                continue

            # Prepare unique key for the vector DB
            # TODO: Add unique user identifier
            key = context.project_name + '/' + file_meta['file']
            key = key.replace('//', '/')
            vector_metadata = {
                "summary": file_meta['summary'],
                "original_location": file_meta['file'],
                "last_updated": datetime.now(timezone.utc).isoformat() + 'Z',
                "project_name": context.project_name,
                "type": "function" if "@" in file_meta['file'] else "file"
            }
            entry = VectorRecord(key, file_meta['summary'], vector_metadata)
            entries.append(entry)
        except Exception as e:
            print(f"Failed to vectorize file at: {file_path}. Error: {e}")
    
    return entries
