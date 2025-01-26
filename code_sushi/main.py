
import argparse
from .core import (
    scan_repo, 
    get_code_insights, 
    embed_and_upload_the_summaries,
    stop_background_loop
)
from .context import Context
from .agents import AgentTeam
from .jobs import JobQueue
from typing import Optional
from .storage import GoogleCloudStorage
import atexit
import os

def dry_run():
    """
    Perform a dry run to show what would be processed without making changes.
    """
    print("Performing a dry run...")

def upload(repo_path: str, log_level: int, workers: int):
    """
    Upload results of the processed repository to a blog storage and vector database.
    """
    context = Context(repo_path=repo_path, log_level=log_level)
    print("Uploading processed repository chunks to Blob Storage...")

    # 1- Upload to GCP
    storage = GoogleCloudStorage(context, concurrent_threads=workers)
    context.output_dir = os.path.abspath(f"{repo_path}/.llm")
    destination_dir = f"{context.project_name}/.llm/"
    storage.bulk_upload(context.output_dir, destination_dir)

def vectorize(repo_path: str, log_level: int):
    """
    Embed the summaries and vectorize them for every file and chunk in disk.
    """

    context = Context(repo_path=repo_path, log_level=log_level)
    context.output_dir = os.path.abspath(f"{repo_path}/.llm")
    
    embed_and_upload_the_summaries(context)
    atexit.register(stop_background_loop)

def slice(repo_path: str, log_level: int, agents: int, limit: Optional[int] = None):
    """
    Slice the repository into chunks for processing.
    """
    context = Context(repo_path=repo_path, log_level=log_level)

    print("Scanning the repository...")
    files = scan_repo(context)

    if limit:
        files = files[-int(limit):]
        print(f"Keeping only the first {limit} files for testing purposes.")

    print(f"\n--\nTotal files selected in repo: {len(files)}\n--\n")

    # Confirm with user the files detected look good
    get_code_insights(files, True)
    confirm = input("\n\nBased on this overview, do you want to proceed with slicing this repo? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborting the slicing process.")
        return
    
    # Prepare output directory
    output_dir = os.path.abspath(f"{repo_path}/.llm")
    clean(output_dir)
    context.output_dir = output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Get to work
    pipeline = JobQueue(context, files)
    team = AgentTeam(context, agent_count=agents)
    team.get_to_work(pipeline)

def clean(output_dir: str):
    """
    Clean up the local output directory after processing.
    """
    print("Cleaning up output directory...")
    os.system(f"rm -rf {output_dir}")
    print("Directory cleaned up.")

def main():
    parser = argparse.ArgumentParser(description="Code Sushi: Slice and organize your code repo for LLMs.")
    subparsers = parser.add_subparsers(dest="command",required=True)

    # Add 'dry-run' command
    dry_run_parser = subparsers.add_parser("dry-run", help="Simulate the slicing process without modifying the repo.")
    dry_run_parser.set_defaults(func=dry_run)

    # Add 'upload' command
    upload_parser = subparsers.add_parser("upload", help="Process the repo and upload the results.")
    upload_parser.add_argument("--path", required=True, help="Path to the repository to process.")
    upload_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    upload_parser.add_argument("--workers", type=int, default=20, help="Number of thread workers to use for parallel uploading.")
    upload_parser.set_defaults(func=upload)

    # Add 'slice' command
    slice_parser = subparsers.add_parser("slice", help="Slice the repo into chunks for processing.")
    slice_parser.add_argument("--path", required=True, help="Path to the repository to process.")
    slice_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    slice_parser.add_argument("--agents", type=int, default=5, help="Number of agents to use for processing.")
    slice_parser.add_argument("--limit", help="Sets a limit to the number of files to process for testing purposes.")
    slice_parser.set_defaults(func=slice)

    # Add 'vectorize' command
    vectorize_parser = subparsers.add_parser("vectorize", help="Embed the summaries and vectorize them for every file and chunk in disk.")
    vectorize_parser.add_argument("--path", required=True, help="Path to the repository to process.")
    vectorize_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")
    vectorize_parser.set_defaults(func=vectorize)

    # Add 'clean' command
    clean_parser = subparsers.add_parser("clean", help="Clean up the repo after processing.")
    clean_parser.set_defaults(func=clean)
    
    # Parse and execute the appropriate command
    args = parser.parse_args()

    if args.command == "slice":
        args.func(args.path, args.log, args.agents, args.limit)
    elif args.command == "upload":
        args.func(args.path, args.log, args.workers)
    elif args.command == "vectorize":
        args.func(args.path, args.log)
    else:
        args.func()

if __name__ == "__main__":
    main()
