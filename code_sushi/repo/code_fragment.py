from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Iterator
from code_sushi.core import File
import os

@dataclass
class CodeFragment:
    """Represents a fragment of code from the repository"""
    path: str
    name: str
    content: str
    start_line: int
    end_line: int
    #commit_hash: str
    summary: Optional[str] = None
    parent_file_summary: Optional[str] = None

    def absolute_path(self) -> str:
        return os.path.abspath(self.path)
    
    def type(self) -> str:
        return "function" if self.parent_file_summary else "file"
    
    @staticmethod
    def from_file(file: File) -> "CodeFragment":
        """
        Create a CodeFragment from a File.
        """
        start_line = 0
        end_line = 0
        content = ""
        try:
            with open(file.absolute_path, 'r') as f:
                end_line = sum(1 for _ in f)
                content = f.read()

            return CodeFragment(file.relative_path, file.file_name, content, start_line, end_line)
        except Exception as e:
            print(f"Error in CodeFragment.from_file(): {e}")
            raise e

class RepoReader(ABC):
    """Interface for reading code from repositories"""
    
    @abstractmethod
    def get_current_files(self) -> Iterator[str]:
        """Get list of all files in current working tree"""
        pass
    
    @abstractmethod
    def read_file(self, path: str, ref: str = 'HEAD') -> str:
        """Read file content at specific ref"""
        pass
    
    @abstractmethod
    def get_file_history(self, path: str) -> List[str]:
        """Get commit history for a file"""
        pass

class GitReader(RepoReader):
    """Git implementation using GitPython"""
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        
    def get_current_files(self) -> Iterator[str]:
        """List all tracked files, respecting .gitignore"""
        for item in self.repo.tree().traverse():
            if item.type == 'blob':  # is a file
                yield item.path
                
    def read_file(self, path: str, ref: str = 'HEAD') -> str:
        """Read file content at specific ref"""
        try:
            return self.repo.git.show(f'{ref}:{path}')
        except git.exc.GitCommandError:
            raise FileNotFoundError(f"File {path} not found at ref {ref}")
