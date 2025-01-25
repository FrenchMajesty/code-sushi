"""
Initialization file for the Core module.

This module contains the primary logic for processing code, organizing
data, and managing outputs.
"""
# Import submodules
from .processor import scan_repo

# Define __all__ for explicit module imports
__all__ = ["scan_repo"]
