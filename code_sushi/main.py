
import argparse
import asyncio
from collections import defaultdict
from .context import Context, LogLevel
from .agents import AgentTeam
from .chat import Chat
from .jobs import JobQueue
from .types import CodeFragment
from .repo import RepoScanner, get_code_insights
from .vector import VectorProcessor
from typing import Optional, List
import atexit
import os
import json
from dotenv import load_dotenv

load_dotenv()

def init(log_level: int):
    """
    Initialize the Code Sushi environment.
    """
    # Create a .sushiignore and sushi-config.json file in the root of the repository
    repo_root = os.path.abspath(os.getcwd())
    sushiignore_path = os.path.join(repo_root, ".sushiignore")
    config_template_path = os.path.join(repo_root, "sushi-config.json.template")
    config_path = os.path.join(repo_root, "sushi-config.json")

    # Copy .sushiignore from package to repo root
    package_sushiignore_path = os.path.join(os.path.dirname(__file__), ".sushiignore")
    if not os.path.exists(sushiignore_path):
        with open(package_sushiignore_path, 'r') as src, open(sushiignore_path, 'w') as dst:
            dst.write(src.read())
        
        if log_level >= LogLevel.DEBUG.value:
            print(f"Created .sushiignore at {sushiignore_path}")        

    # Copy sushi-config.json.template from package to repo root and rename it
    package_config_template_path = os.path.join(os.path.dirname(__file__), "sushi-config.json.template")
    if not os.path.exists(config_path):
        with open(package_config_template_path, 'r') as src, open(config_template_path, 'w') as dst:
            dst.write(src.read())
        os.rename(config_template_path, config_path)

        if log_level >= LogLevel.DEBUG.value:
            print(f"Created sushi-config.json at {config_path}")

    # Add the config file to the .gitignore file
    with open(os.path.join(repo_root, ".gitignore"), 'a') as gitignore:
        gitignore.write("\nsushi-config.json\n")

    print("Code Sushi environment ready.")

def read_config_into_context(args: argparse.Namespace) -> Context:
    """
    Read the configuration from the sushi-config.json file into the context.
    """
    curr_dir = os.path.abspath(os.getcwd())

    config_path = os.path.join(os.path.abspath(os.getcwd()), "sushi-config.json")

    if not os.path.exists(config_path) and "path" not in args and args.command != "init":
        raise FileNotFoundError(f"Configuration file not found at {config_path} and no --path arg provided. Please run 'sushi init' or add --path argument.")

    config_data = defaultdict()
    try:
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            context.has_config_file = True
    except Exception as e:
        if args.log >= LogLevel.DEBUG.value:
            print(f"Error reading config file: {e}")

    context = Context(curr_dir)
    context.vector_db_concurrent_limit = config_data.get("vector_db_max_concurrent_requests", 25)
    context.max_agents = config_data.get("max_agents", 10)
    context.embedding_model_chunk_size = config_data.get("embedding_max_chunk_size", 128)
    
    # Add third party services configs
    context.ai_provider = config_data.get("ai_provider", "together")
    context.vector_db_provider = config_data.get("vector_db_provider", "pinecone")
    context.embedding_provider = config_data.get("embedding_provider", "voyage")
    context.together_ai_config = config_data.get("together_ai", None)
    context.voyage_ai_config = config_data.get("voyage_ai", None)
    context.openai_config = config_data.get("openai", None)
    context.svector_config = config_data.get("svector", None)
    context.pinecone_config = config_data.get("pinecone", None)
    
    # Handle user-provided arguments
    if "log" in args and args.log:
        context.log_level = LogLevel(args.log)
    
    if "path" in args and args.path:
        context.repo_path = os.path.abspath(args.path)
    
    if "agents" in args and args.agents:
        context.max_agents = args.agents

    if "vector_workers" in args and args.vector_workers:
        context.vector_db_concurrent_limit = args.vector_workers
    
    if "embed_chunks" in args and args.embed_chunks:
        context.embedding_model_chunk_size = args.embed_chunks
    
    if "stream" in args and args.stream:
        context.stream_chat_response = True
    
    output_dir = os.path.abspath(f"{context.repo_path}/.llm/")
    context.output_dir = output_dir
    
    if context.is_log_level(LogLevel.DEBUG):
        print(f"Context ready: {context.overview()}")   

    return context
    
def run(context: Context, limit: Optional[int] = None):
    """
    Process the repository and upload the results.
    """
    fragments = slice(context, limit)
    if not fragments:
        return

    VectorProcessor(context).embed_and_upload_summaries(fragments)

def slice(context: Context, limit: Optional[int] = None) -> Optional[List[CodeFragment]]:
    """
    Slice the repository into chunks for processing.
    """
    print("Scanning the repository...")
    scanner = RepoScanner(context)
    files = scanner.scan_repo()

    if limit:
        files = files[-int(limit):]
        print(f"Keeping only the first {limit} files for testing purposes.")

    print(f"\n--\nTotal files selected in repo: {len(files)}\n--\n")

    # Confirm with user the files detected look good
    get_code_insights(files, True)
    confirm = input("\n\nBased on this overview, do you want to proceed with slicing this repo? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborting the slicing process.")
        return None
    
    # Get to work
    os.makedirs(context.output_dir, exist_ok=True)
    queue = JobQueue(context, files)
    team = AgentTeam(context)
    team.get_to_work(queue)

    final = [f for f in team.fragments_done.values() if f.summary]
    return final
    
def clean(context: Context):
    """
    Clean up the local output directory after processing.
    """
    print("Cleaning up output directory...")
    os.system(f"rm -rf {context.output_dir}")
    print("Directory cleaned up.")

def chat(context: Context):
    """
    Start the chatbot interface for Code Sushi.
    """
    chat = Chat(context)
    if context.stream_chat_response:
        asyncio.run(chat.start_session_stream())
    else:
        chat.start_session()

def ask(context: Context, question: str):
    """
    Ask a single question about the codebase and get an answer.
    """
    chat = Chat(context)
    question = " ".join(question)

    if context.stream_chat_response:
        asyncio.run(chat.ask_question_stream(question))
    else:
        chat.ask_question(question)

def main():
    parser = argparse.ArgumentParser(description="Code Sushi: Slice and organize your code repo for LLMs.")
    subparsers = parser.add_subparsers(dest="command",required=True)

    # Add 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize the Code Sushi environment.")
    init_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    init_parser.set_defaults(func=init)

    # Add 'run' command
    run_parser = subparsers.add_parser("run", help="Process the repo and upload the results.")
    run_parser.add_argument("--path", default="./", help="Path to the repository to process.")
    run_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    run_parser.add_argument("--limit", help="Sets a limit to the number of files to process for testing purposes.")
    run_parser.add_argument("--agents", type=int, default=10, help="Number of AI agents to use for summarizing files.")
    run_parser.add_argument("--vector-workers", type=int, default=25, help="Number of thread workers to use for parallel vectorizing.")
    run_parser.add_argument("--embed-chunks", type=int, default=128, help="Number of items per batch for embedding requests.")
    run_parser.set_defaults(func=run)

    # Add 'slice' command
    slice_parser = subparsers.add_parser("slice", help="Slice the repo into chunks for processing.")
    slice_parser.add_argument("--path", help="Path to the repository to process.")
    slice_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    slice_parser.add_argument("--agents", type=int, default=10, help="Number of AI agents to use for summarizing files.")
    slice_parser.add_argument("--limit", help="Sets a limit to the number of files to process for testing purposes.")
    slice_parser.set_defaults(func=slice)

    # Add 'clean' command
    clean_parser = subparsers.add_parser("clean", help="Clean up the repo after processing.")
    clean_parser.set_defaults(func=clean)

    # Add 'chat' command
    chat_parser = subparsers.add_parser("chat", help="Start the chatbot interface for Code Sushi.")
    chat_parser.add_argument("--path", help="Path to the repository to process.")
    chat_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    chat_parser.add_argument("--stream", default=True, help="Stream the response from the LLM.")
    chat_parser.set_defaults(func=chat)

    # Add 'ask' command
    ask_parser = subparsers.add_parser("ask", help="Ask a single question to the LLM.")
    ask_parser.add_argument("question", nargs="+", help="The question to ask the LLM")
    ask_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    ask_parser.add_argument("--stream", default=True, help="Stream the response from the LLM.")
    ask_parser.set_defaults(func=ask)

    # Parse and execute the appropriate command
    args = parser.parse_args()
    context = read_config_into_context(args)

    if args.command == "init":
        args.func(args.log)
    elif args.command == "slice":
        args.func(context, args.limit)
    elif args.command == "run":
        args.func(context, args.limit)
    elif args.command == "ask":
        args.func(context, args.question)
    else:
        args.func(context)

if __name__ == "__main__":
    main()
