from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Iterator

@dataclass
class CodeFragment:
    """Represents a fragment of code from the repository"""
    path: str
    name: str
    content: str
    start_line: int
    end_line: int
    #commit_hash: str
    parent_file_summary: Optional[str] = None

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
