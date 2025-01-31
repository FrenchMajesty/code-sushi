from typing import List, Optional
import os
from concurrent.futures import ThreadPoolExecutor
from code_sushi.context import Context, LogLevel
from code_sushi.core import File
from code_sushi.vector import VectorRecord
from pathspec import PathSpec
import pathspec
from datetime import datetime, timezone
from .is_code_file_filter import is_code_file
from .utils import (
    print_details,
    get_files_from_folder,
    get_code_insights,
    extract_metadata_from_output_file
)

"""
RepoScanner module for Code Sushi.

This module handles scanning repositories to find relevant files for processing.
"""

class RepoScanner:
    """
    Scanner class responsible for finding and processing repository files.
    """
    def __init__(self, context: Context):
        self.context = context

    def scan_repo(self) -> List[File]:
        """
        Scan the repository for files to process.
        """
        # Shallow pass: list content at root level
        dirs = self.shallow_root_scan()
        files = self.get_root_files()

        # Deep pass: list content in subdirectories
        for directory in dirs:
            sub_files = get_files_from_folder(directory)
            files.extend(sub_files)

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"{len(sub_files)} files found in {directory}")
        
        files = self.filter_out_bad_files(files)

        # Convert to File objects
        files = [File(self.context.repo_path, file) for file in files]

        if self.context.log_level.value >= LogLevel.VERBOSE.value:
            print_details(files)
        
        return files

    def shallow_root_scan(self) -> List[str]:
        """
        Shallow scan the root of repository for directories to process while ignoring bad directories.
        """
        dirs = [d for d in os.listdir(self.context.repo_path) if os.path.isdir(os.path.join(self.context.repo_path, d))]
        dirs = self.filter_out_bad_dirs(dirs)

        dirs = [os.path.abspath(os.path.join(self.context.repo_path, d)) for d in dirs]

        return dirs

    def get_root_files(self) -> List[str]:
        """
        Get the root files in the repository.
        """
        files = [
            os.path.abspath(os.path.join(self.context.repo_path, f))
            for f in os.listdir(self.context.repo_path)
            if os.path.isfile(os.path.join(self.context.repo_path, f))
        ]
        
        return files

    def load_ignore_patterns(self, name: str) -> Optional[PathSpec]:
        """
        Loads patterns from a .gitignore-type file to know which files/folders to skip.
        """
        path = '/'.join([self.context.repo_path, name])
        found = False
        try:
            with open(path, "r") as gitignore_file:
                found = True
                gitignore_patterns = gitignore_file.read()
            spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns.splitlines())
        except FileNotFoundError:
            spec = None

        if self.context.is_log_level(LogLevel.VERBOSE):
            print(f"Found {name} file? {found}")
        
        return spec

    def filter_out_bad_dirs(self, dirs: List[str]) -> List[str]:
        """
        Filter out the directories that are not useful or desirable for processing.
        """
        show_debug = self.context.is_log_level(LogLevel.DEBUG)

        if show_debug:
            print(f"\n--> Filtering out bad directories. Starting at {len(dirs)}")

        # Filter out paths that match regex lines in .gitignore
        gitignore = self.load_ignore_patterns(".gitignore")
        if gitignore:
            dirs = [dir for dir in dirs if not gitignore.match_file(dir + '/')]

            if show_debug:
                print(f"After .gitignore: {len(dirs)}")

        # Use .sushiignore to filter out directories
        sushiignore = self.load_ignore_patterns(".sushiignore")
        if sushiignore:
            dirs = [dir for dir in dirs if not sushiignore.match_file(dir + '/')]

            if show_debug:
                print(f"After .sushiignore: {len(dirs)}")

        # Ignore content in .git/ or .llm/ directory
        dirs = [dir for dir in dirs if dir != ".git" and dir != ".llm"]

        if show_debug:
            print(f"Final dirs count: {len(dirs)}")

        return dirs

    def filter_out_bad_files(self, files: List[str]) -> List[str]:
        """
        Filter out the files that are not useful or desirable for processing.
        """
        show_debug = self.context.is_log_level(LogLevel.DEBUG)
        if show_debug:
            print(f"\n --> Filtering out bad files. Starting at {len(files)}")

        # Apply .gitignore and .sushiignore filters
        for ignore_file in [".gitignore", ".sushiignore"]:
            ignore_patterns = self.load_ignore_patterns(ignore_file)
            if ignore_patterns:
                files = list(ignore_patterns.match_files(files, negate=True))
                if show_debug:
                    print(f"After {ignore_file}: {len(files)}")

        # Filter to only code files
        files = [f for f in files if is_code_file(f)]
        if show_debug:
            print(f"After file extension check: {len(files)}")

        return files
