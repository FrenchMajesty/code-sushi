import os

class File:
    """
    Represents a file in the repository.
    """

    def __init__(self, repo_root: str, path: str):
        self.absolute_path = os.path.abspath(path)
        self.clean_path = path.replace(repo_root, "", 1)
        self.file_name = os.path.basename(self.clean_path)

        # Get metadata about the file
        self.line_count = sum(1 for _ in open(self.absolute_path))
        self.file_size = os.path.getsize(self.absolute_path)

    def __str__(self):
        return '\t'.join([
            f"{self.line_count:,} lines",
            f"{self.file_size} bytes",
            self.clean_path
        ])
