"""
Initialization file for the Core module.

This module contains the primary logic for processing code, organizing
data, and managing outputs.
"""
# Import submodules
from .processor import scan_repo, write_summary
from .utils import get_code_insights
from .file import File

# Define __all__ for explicit module imports
__all__ = ["scan_repo", "get_code_insights", "File", "write_summary"]
