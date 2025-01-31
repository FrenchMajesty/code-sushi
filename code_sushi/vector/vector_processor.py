from typing import List
from code_sushi.context import Context, LogLevel
from code_sushi.vector import Voyage, VectorRecord, Pinecone
from code_sushi.multi_task import background_loop
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

    def embed_and_upload_the_summaries_from_disk(self):
        """
        Parses the summaries for every file and chunk written to disk to vectorize them.
        """
        files = self.context.get_files_in_output_dir()

        if self.context.is_log_level(LogLevel.INFO):
            print(f"Preparing to embed {len(files)} files...")

        chunk_size = 128
        chunk_idx = 0
        total_chunks = math.ceil(len(files) / chunk_size)
        for i in range(0, len(files), chunk_size):
            chunk_idx += 1
            chunk = files[i:i + chunk_size]
            
            if self.context.is_log_level(LogLevel.INFO):
                print(f"Processing chunk {chunk_idx} of {total_chunks}")

            entries = self._convert_files_to_vector_records(chunk)

            # Mass-embed the text from the entries
            raw_contents = [entry.text for entry in entries]

            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Send req. to embed {len(raw_contents)} text sections")

            embeddings = self.voyage.embed(raw_contents)
            
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Received {len(embeddings)} embeddings back")

            if len(embeddings) != len(entries):
                print(f"Error: Embeddings length {len(embeddings)} does not match entries length {len(entries)}")
                continue
            
            # Assign the embeddings to the linked entries
            for i in range(len(entries)):
                entries[i].embedding = embeddings[i]

            # Upload to vector DB
            self.vector_db.write_many(entries)
