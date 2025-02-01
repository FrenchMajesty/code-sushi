from code_sushi.context import Context, LogLevel
from code_sushi.agents import ModelClient
from code_sushi.repo import CodeSearcher
import time
import sys

class Chat:
    def __init__(self, context: Context):
        self.context = context
        self.history = []
        self.code_searcher = CodeSearcher(context)
        self.model_client = ModelClient(context)

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
                
                contexts = self.code_searcher.search(user_query)
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
            contexts = self.code_searcher.search(question)
            
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
