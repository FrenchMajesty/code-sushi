"""
Initialization file for the Core module.

This module contains the primary logic for processing code, organizing
data, and managing outputs.
"""
# Import submodules
from .processor import (
    write_summary_to_file, 
)
from .file import File

# Define __all__ for explicit module imports
__all__ = [
    "File",
    "write_summary_to_file",
]
