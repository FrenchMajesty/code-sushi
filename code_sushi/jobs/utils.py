from typing import List
from code_sushi.core import File

# Define weights for different signals
PATH_WEIGHTS = {
    "controllers": 5,
    "services": 5,
    "routes": 4,
    "src": 3,
    "module": 3,
    "tests": -3,
    "docs": -2,
    "node_modules": -5,
    "build": -5,
}
NAME_WEIGHTS = {
    "main": 5,
    "app": 5,
    "index": 4,
    "controller": 4,
    "service": 4,
    "router": 4,
    "test": -3,
    "example": -3,
    "readme": -2,
}
EXT_WEIGHTS = {
    ".md": -2,
    ".json": -1,
    ".yml": -2,
    ".yaml": -2,
    ".txt": -2,
}

def calculate_priority(file: File) -> int:
    score = 0

    # Check file path for directory signals
    for dir_name, weight in PATH_WEIGHTS.items():
        if dir_name in file.absolute_path:
            score += weight

    # Check file name signals
    for name, weight in NAME_WEIGHTS.items():
        if name in file.file_name.lower():
            score += weight

    # Check file extension signals
    if file.ext in EXT_WEIGHTS:
        score += EXT_WEIGHTS[file.ext]

    # Add file size as a heuristic (optional)
    if file.size > 0 and file.size < 5000:  # Files under 5KB are likely small logic files
        score += 1
    elif file.size > 100000:  # Large files may be less critical
        score -= 1

    return score

def prioritize_files(files: List[File]) -> List[tuple[int, File]]:
    # Calculate priority for each file
    prioritized_files = [(calculate_priority(file), file) for file in files]
    # Sort files by priority score in descending order
    prioritized_files.sort(key=lambda x: x[0], reverse=True)

    return prioritized_files
