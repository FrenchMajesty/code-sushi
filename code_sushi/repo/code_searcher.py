from typing import List, Dict, Any
from code_sushi.context import Context, LogLevel
from code_sushi.types import CodeFragment
from code_sushi.repo.repo_scanner import RepoScanner
from code_sushi.vector import VectorClient
from code_sushi.embedding import Voyage
import time

class CodeSearcher:
    """
    Handles code search and retrieval.
    """
    
    def __init__(self, context: Context):
        self.context = context
        self.repo_scanner = RepoScanner(context)
        self.vector_client = VectorClient(context)
        self.voyage = Voyage(context)
    
    def search(self, query: str, top_k: int = 6) -> tuple[List[str], List[CodeFragment]]:
        """
        Find the most relevant code snippets for the query.
        """
        try:
            start = time.time()
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Searching for context on query: [{query}] ...")

            # Run RAG search
            vector_query = self.voyage.embed([query])[0]
            search_results = self.vector_client.search(vector_query, top_k=top_k)

            # Read the code matching vector records
            fragments = [CodeFragment.from_rag_search(hit) for hit in search_results]
            contents = [self.repo_scanner.read_fragment_content(f) for f in fragments]

            # Run rerank
            reranked = self.voyage.rerank(query, contents, top_k=max(3, top_k // 2))

            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start
                print(f"Took {runtime:.2f} seconds to pick best {len(reranked)} documents")
                
                if self.context.is_log_level(LogLevel.VERBOSE):
                    print(reranked)

            # Match up with original fragments
            matched_fragments = self._match_reranked_content(reranked, contents, fragments)

            return reranked, matched_fragments
        except Exception as e:
            print(f"Error in CodeSearcher.search(): {e}")
            return []
        
    def _match_reranked_content(self, reranked: List[str], contents: List[str], fragments: List[CodeFragment]) -> List[CodeFragment]:
        """
        Match reranked content back to original fragments.
        """
        matched = []
        for reranked_content in reranked:
            # Find index of this content in original contents list
            try:
                idx = contents.index(reranked_content)
                matched.append(fragments[idx])
            except ValueError:
                # Content not found in original list, skip it
                continue
        return matched
