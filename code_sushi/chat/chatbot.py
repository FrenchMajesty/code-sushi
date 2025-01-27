import pinecone
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from code_sushi.context import Context, LogLevel
from code_sushi.agents import format_query_for_rag
import requests
import os
import signal
import sys


# Initialize Pinecone and define constants
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_ENVIRONMENT = "your-pinecone-environment"
INDEX_NAME = "your-index-name"
RERANK_API_URL = "your-rerank-api-url"  # Replace with your rerank endpoint
OPENAI_API_KEY = "your-openai-api-key"

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
vectorstore = Pinecone.from_existing_index(index_name=INDEX_NAME, embedding_function=None)

# Initialize OpenAI LLM
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

# Define RAG Chat Functionality
def rerank_results(results):
    """Send Pinecone results to a rerank API."""
    response = requests.post(RERANK_API_URL, json={"results": results})
    response.raise_for_status()
    return response.json()["reranked_results"]


def start_chat_session(context: Context):
    """Start an interactive chat session."""
    print("Sushi Chat - Ask your questions below. Press Ctrl+C to exit.")
    query_template = PromptTemplate(template="{question}\n\nRelevant context:\n{context}", input_variables=["question", "context"])
    retriever = vectorstore.as_retriever()

    chain = ConversationalRetrievalChain(
        retriever=retriever,
        llm=llm,
        combine_docs_chain_kwargs={"prompt": query_template},
    )

    history = []
    while True:
        try:
            user_query = input("You: ")
            if not user_query.strip():
                continue

            formatted_query = format_query_for_rag(context, user_query)
            raw_results = retriever.get_relevant_documents(formatted_query)

            # Send results to rerank API
            reranked_results = rerank_results(raw_results)
            selected_context = "\n".join([res["text"] for res in reranked_results[:3]])

            # Generate response
            response = chain.run({"question": user_query, "context": selected_context, "history": history})
            history.append({"question": user_query, "answer": response})

            print(f"AI: {response}")
        except KeyboardInterrupt:
            print("\nExiting Sushi Chat. Goodbye!")
            sys.exit(0)
