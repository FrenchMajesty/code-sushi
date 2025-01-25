import os

class File:
    """
    Represents a file in the repository.
    """

    def __init__(self, repo_root: str, path: str):
        self.absolute_path = os.path.abspath(path)
        self.clean_path = path.replace(repo_root, "", 1)
        self.file_name = os.path.basename(self.clean_path)
        self.ext = os.path.splitext(self.clean_path)[1]

        # Get metadata about the file
        try:
            self.line_count = sum(1 for _ in open(self.absolute_path))
            self.file_size = os.path.getsize(self.absolute_path)
        except Exception as e:
            print(f"Error reading file: {self.absolute_path}. {e}")
            exit(1)

    def __str__(self):
        return '\t'.join([
            f"{self.line_count:,} lines",
            f"{self.file_size} bytes",
            self.clean_path
        ])
