from typing import List
from code_sushi.context import Context, LogLevel
from code_sushi.vector import Voyage, VectorRecord, Pinecone
from code_sushi.multi_task import background_loop
from code_sushi.repo import CodeFragment
from datetime import datetime, timezone
from .utils import chunks
import math

class VectorProcessor:
    """
    Handles vectorization and uploading of code fragments and file summaries to vector databases.
    """
    def __init__(self, context: Context):
        self.context = context
        self.voyage = Voyage(context)
        self.vector_db = Pinecone(context)
    
    def embed_and_upload_summaries(self, fragments: List[CodeFragment]) -> None:
        """
        Embeds and uploads summaries from a list of code fragments to the vector database.
        """
        if not fragments:
            return

        background_loop.start()

        if self.context.is_log_level(LogLevel.INFO):
            print(f"Preparing to embed {len(fragments)} fragments...")

        # Process fragments in chunks
        for chunk in chunks(fragments, 128):
            if not chunk:
                continue
            
            entries = VectorRecord.from_fragments(chunk, self.context.project_name)
            raw_contents = [entry.text for entry in entries]
            embeddings = self.voyage.embed(raw_contents)
            
            if not embeddings or len(embeddings) != len(entries):
                print(f"Error: Embeddings length {len(embeddings)} does not match entries length {len(entries)}")
                continue

            # Assign the embeddings to the linked entries
            for i in range(len(entries)):
                entries[i].embedding = embeddings[i]

            # Upload to vector DB
            self.vector_db.write_many(entries)

        background_loop.stop()
