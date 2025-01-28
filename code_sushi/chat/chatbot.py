from code_sushi.vector import Pinecone, VoyageEmbed
from code_sushi.context import Context, LogLevel
from code_sushi.agents import format_query_for_rag
import requests
import os
import signal
import sys


def start_chat_session(context: Context):
    """Start an interactive chat session."""
    print("Sushi Chat - Ask your questions below. Press Ctrl+C to exit.")
    #query_template = PromptTemplate(template="{question}\n\nRelevant context:\n{context}", input_variables=["question", "context"])
    pinecone = Pinecone()
    voyage = VoyageEmbed()

    history = []
    while True:
        try:
            user_query = input("You: ")
            if not user_query.strip():
                continue

            formatted_query = format_query_for_rag(context, user_query)
            print("Formatted query:", formatted_query)
            vector_query = voyage.embed([formatted_query])[0]
            raw_results = pinecone.search(vector_query)
            print("Raw results:", raw_results)
            #raw_results = retriever.get_relevant_documents(formatted_query)

            # Send results to rerank API
            reranked_results = voyage.rerank(user_query, raw_results)
            selected_context = "\n".join([res["text"] for res in reranked_results[:3]])

            print("Selected context:", selected_context)

            # Generate response
            #response = chain.run({"question": user_query, "context": selected_context, "history": history})
            #history.append({"question": user_query, "answer": response})

            #print(f"AI: {response}")
        except KeyboardInterrupt:
            print("\nExiting Sushi Chat. Goodbye!")
            sys.exit(0)
