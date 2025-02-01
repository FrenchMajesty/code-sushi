from code_sushi.vector import Pinecone, Voyage
from code_sushi.context import Context, LogLevel
from code_sushi.agents import ModelClient
from code_sushi.repo import CodeFragment, RepoScanner
from typing import List
import time
import sys

class Chat:
    def __init__(self, context: Context):
        self.context = context
        self.history = []
        self.pinecone = Pinecone(context)
        self.voyage = Voyage(context)
        self.model_client = ModelClient(context)
        self.repo_scanner = RepoScanner(context)

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
                self.history.append({
                    "role": "user",
                    "content": user_query
                })

                req = self.history + [{
                    "role": "user",
                    "content": "--CONTEXT--\n" + "\n".join(contexts)
                }]

                # Generate response
                response = self.model_client.send_completion_request(req)
                self.history.append({
                    "role": "assistant",
                    "content": response
                })
                print(f"AI: {response}")
                print("-" * 80)
            except KeyboardInterrupt:
                print("\nExiting Sushi Chat. Goodbye!")
                sys.exit(0)
    
    def ask_question(self, question: str):
        """
        Ask a single question and get a response.
        """
        try:
            start = time.time()
            print(f"User aked: {question}")
            contexts = self.find_context(question)
            
            messages = [{
                "role": "user", 
                "content": question
            }, {
                "role": "user",
                "content": f"--PROJECT {self.context.project_name} CONTEXT--\n" + "\n".join(contexts)
            }]

            response = self.model_client.send_completion_request(messages)
            print(f"AI: {response}")

            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start
                print(f"Took {runtime:.2f} sec to answer question.")

        except Exception as e:
            print(f"Error in Chat.ask_question(): {e}")

    def find_context(self, query: str) -> List[str]:
        """
        Find the most relevant context snippets for the query.
        """
        try:
            start = time.time()
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Searching for context on query: [{query}] ...")

            #formatted_query = format_query_for_rag(self.context, query) TODO: Use a formatted query
            vector_query = self.voyage.embed([query])[0]
            search_results = self.pinecone.search(vector_query, top_k=6)
            fragments = [CodeFragment.from_rag_search(hit) for hit in search_results]
            contents = [self.repo_scanner.read_fragment_content(f) for f in fragments]
            reranked = self.voyage.rerank(query, contents, top_k=3)

            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start
                print(f"Took {runtime:.2f} seconds to pick best {len(reranked)} documents")
                
                if self.context.is_log_level(LogLevel.VERBOSE):
                    print(reranked)

            return reranked
        except Exception as e:
            print(f"Error in Chat.find_context(): {e}")
            return []
