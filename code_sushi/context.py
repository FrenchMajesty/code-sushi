from typing import Optional

class Context:
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_language: Optional[str] = None
        self.repo_path: Optional[str] = repo_path
