from code_sushi.vector import Pinecone, VoyageEmbed
from code_sushi.context import Context, LogLevel
from code_sushi.agents import format_query_for_rag
from typing import List
import sys

class Chat:
    def __init__(self, context: Context):
        self.context = context
        self.history = []
        self.pinecone = Pinecone(context)
        self.voyage = VoyageEmbed()

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
            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Searching for on query: {query}...")

            #formatted_query = format_query_for_rag(self.context, query)
            vector_query = self.voyage.embed([query])[0]
            raw_results = self.pinecone.search(vector_query)
            reranked_results = self.voyage.rerank(query, raw_results)
            selected_context = [res["text"] for res in reranked_results]
            return selected_context
        except Exception as e:
            print(f"Error in Chat.find_context(): {e}")
            return []
