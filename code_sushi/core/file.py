import os

class File:
    """
    Represents a file in the repository.
    """

    def __init__(self, repo_root: str, path: str):
        self.absolute_path = os.path.abspath(path)
        self.relative_path = path.replace(repo_root, "", 1)
        self.file_name = os.path.basename(self.relative_path)
        self.ext = os.path.splitext(self.relative_path)[1]
        self.size = 0
        self.line_count = 0

        if len(path) > len(repo_root):
            self.sanitize_relative_path(repo_root)

        self.load_metadata()

    def sanitize_relative_path(self, repo_root: str):
        """
        Sanitize the clean path on potentially malformed files in root folder.
        """
        last_part = repo_root.split("/")[-1]
        if last_part in self.relative_path:
            self.relative_path = self.relative_path.split(last_part, 1)[1]

    def load_metadata(self):
        """
        Load metadata for the file.
        """
        try:
            self.line_count = sum(1 for _ in open(self.absolute_path))
            self.size = os.path.getsize(self.absolute_path)
        except Exception as e:
            print(f"Error reading file: {self.absolute_path}. {e}")
            exit(1)

    def __str__(self):
        return '\t'.join([
            f"{self.line_count:,} lines",
            f"{self.size} bytes",
            self.relative_path
        ])
