class CodeSearcher:
    """
    Handles code search and retrieval
    """
    
    def __init__(self,
                 repo_reader: RepoReader,
                 vector_store: PGVectorStore,
                 embedding_service: EmbeddingService):
        self.repo_reader = repo_reader
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant code snippets"""
        # Generate query embedding
        query_embedding = await self.embedding_service.embed(query)
        
        # Search vector store
        results = self.vector_store.search_similar(query_embedding, top_k)
        
        # Enhance results with current file content
        enhanced_results = []
        for result in results:
            try:
                current_content = self.repo_reader.read_file(result['file_path'])
                result['current_content'] = self._extract_snippet(
                    current_content,
                    result['metadata']['start_line'],
                    result['metadata']['end_line']
                )
                enhanced_results.append(result)
            except FileNotFoundError:
                # File was deleted or moved
                continue
                
        return enhanced_results
