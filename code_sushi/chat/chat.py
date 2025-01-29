from code_sushi.vector import Pinecone, Voyage
from code_sushi.context import Context, LogLevel
from code_sushi.agents import format_query_for_rag
from code_sushi.storage import  GoogleCloudStorage
from typing import List
import time
import sys

class Chat:
    def __init__(self, context: Context):
        self.context = context
        self.history = []
        self.pinecone = Pinecone(context)
        self.voyage = Voyage(context)

    def start_session(self):
        """
        Start an interactive chat session.
        """
        print("Sushi Chat - Ask your questions below. Press Ctrl+C to exit.")

        while True:
            try:
                user_query = input("You: ")
                if not user_query.strip():
                    continue
                
                contexts = self.find_context(user_query)

                # Generate response
                #response = chain.run({"question": user_query, "context": selected_context, "history": history})
                #history.append({"question": user_query, "answer": response})

                #print(f"AI: {response}")
            except KeyboardInterrupt:
                print("\nExiting Sushi Chat. Goodbye!")
                sys.exit(0)
    
    def find_context(self, query: str) -> List[str]:
        """
        Find the most relevant context snippets for the query.
        """
        try:
            start = time.time()
            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Searching for context on query: [{query}] ...")

            storage = GoogleCloudStorage(self.context)

            #formatted_query = format_query_for_rag(self.context, query) TODO: Use a formatted query
            vector_query = self.voyage.embed([query])[0]
            search_results = self.pinecone.search(vector_query)
            base_storage_path = self.context.project_name + '/.llm/'
            paths = [base_storage_path + hit['original_location'] + '.md' for hit in search_results]
            relevant_files_content = storage.read_many_files(paths)
            reranked = self.voyage.rerank(query, relevant_files_content)

            if self.context.log_level.value >= LogLevel.DEBUG.value:
                runtime = time.time() - start
                print(f"Took {runtime:.2f} seconds to pick best {len(reranked)} documents")
                
                if self.context.log_level.value >= LogLevel.VERBOSE.value:
                    print(reranked)

            return reranked
        except Exception as e:
            print(f"Error in Chat.find_context(): {e}")
            return []
