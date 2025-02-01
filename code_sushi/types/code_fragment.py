from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Iterator
from .file import File
from .vector_record import VectorRecord
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
    
    def to_vector_record(self, project_name: str) -> VectorRecord:
        """
        Create a VectorRecord from this CodeFragment.
        
        Args:
            project_name: Name of the project
        
        Returns:
            VectorRecord object representing this fragment
        """
        from datetime import datetime, timezone

        key = f"{project_name}/{self.path}".replace('//', '/')
        if self.type() == "function":
            key = f"{key}@{self.name}".replace('//', '/')

        last_updated = datetime.now(timezone.utc).isoformat() + 'Z'
        metadata = {
            "summary": self.summary,
            "original_location": self.path,
            "last_updated": last_updated,
            "project_name": project_name,
            "type": self.type(),
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "parent_summary": self.parent_file_summary
        }
        # Strip metadata that are null
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return VectorRecord(key, self.summary, metadata)

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
    
    @staticmethod
    def from_rag_search(record: VectorRecord) -> "CodeFragment":
        """
        Create a CodeFragment from a RAG search result.
        """
        try:
            metadata = record.metadata
            return CodeFragment(
                path=metadata['original_location'],
                name=metadata['name'],
                content=record.text,
                start_line=int(metadata.get('start_line', 0)),
                end_line=int(metadata.get('end_line', 0)),
                summary=metadata.get('summary'),
                parent_file_summary=metadata.get('parent_summary'),
            )
        except Exception as e:
            print(f"Error in CodeFragment.from_rag_search(): {e}")
            raise e
'''
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
'''
