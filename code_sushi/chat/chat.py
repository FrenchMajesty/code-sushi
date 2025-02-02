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
                
                print("-" * 80)
                contexts, fragments = self.code_searcher.search(user_query)
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

                # Show context sources
                sources = []
                for fragment in fragments:
                    source_str = ""
                    if fragment.type() == "function":
                        source_str = f"{fragment.path}@{fragment.name} -> L:{fragment.start_line}:{fragment.end_line}"
                    else:
                        source_str = f"{fragment.path} -> L:{fragment.start_line}:{fragment.end_line}"
                    sources.append(source_str)

                print("-" * 80)
                print("Context sources:", sources)
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
            print('-' * 12)
            print(f"User aked: {question}")
            contexts, fragments = self.code_searcher.search(question)
            
            messages = [{
                "role": "user", 
                "content": question
            }, {
                "role": "user",
                "content": f"--PROJECT {self.context.project_name} CONTEXT--\n" + "\n".join(contexts)
            }]

            response = self.model_client.send_completion_request(messages)
            print('-' * 12)
            print(f"AI: {response}")

            # Format context
            sources = []
            for fragment in fragments:
                source_str = ""
                if fragment.type() == "function":
                    source_str = f"{fragment.path}@{fragment.name} -> L:{fragment.start_line}:{fragment.end_line}"
                else:
                    source_str = f"{fragment.path} -> L:{fragment.start_line}:{fragment.end_line}"

                sources.append(source_str)
            print('-' * 12)
            print("Context sources:", sources)
            print('-' * 12)

            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start
                print(f"Took {runtime:.2f} sec to answer question.")

        except Exception as e:
            print(f"Error in Chat.ask_question(): {e}")
