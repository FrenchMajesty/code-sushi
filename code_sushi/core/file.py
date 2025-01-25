import os

class File:
    """
    Represents a file in the repository.
    """

    def __init__(self, repo_root: str, path: str):
        self.absolute_path = os.path.abspath(path)
        self.clean_path = path.replace(repo_root, "", 1)
        self.file_name = os.path.basename(self.clean_path)

    def __str__(self):
        file_size = os.path.getsize(self.absolute_path)
        loc = sum(1 for _ in open(self.absolute_path))

        return '\t'.join([
            str(loc) + " lines",
            str(file_size) + " bytes",
            self.clean_path
        ])
