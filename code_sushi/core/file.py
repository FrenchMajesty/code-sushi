import os

class File:
    """
    Represents a file in the repository.
    """

    def __init__(self, repo_root: str, path: str):
        self.absolute_path = os.path.abspath(path)
        self.relative_path = ''
        self.file_name = os.path.basename(self.relative_path)
        self.ext = os.path.splitext(path)[1]
        self.size = 0
        self.line_count = 0

        self.sanitize_relative_path(repo_root)
        self.load_metadata()

    def load_metadata(self):
        """
        Load metadata for the file.
        """
        try:
            self.line_count = sum(1 for _ in open(self.absolute_path))
            self.size = os.path.getsize(self.absolute_path)
        except Exception as e:
            print(f"Error reading file into memory: {self.absolute_path}. {e}")
            exit(1)

    def __str__(self):
        return '\t'.join([
            f"{self.line_count:,} lines",
            f"{self.size} bytes",
            self.relative_path
        ])

    def sanitize_relative_path(self, root: str):
        """
        Sanitize the relative path of the file.
        """
        common = os.path.commonprefix([root, self.absolute_path])
        self.relative_path = self.absolute_path.replace(common, "", 1)

        if self.relative_path.startswith("/"):
            self.relative_path = self.relative_path[1:]
