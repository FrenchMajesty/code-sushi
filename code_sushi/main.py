
import argparse
from .core import scan_repo, get_code_insights
from .context import Context, LogLevel
import os

def dry_run():
    """
    Perform a dry run to show what would be processed without making changes.
    """
    print("Performing a dry run...")

def upload():
    """
    Process the repository and upload results to the destination.
    """
    print("Uploading processed repository chunks to RAG system...")

def slice(repo_path: str, log_level: int):
    """
    Slice the repository into chunks for processing.
    """
    context = Context(repo_path=repo_path, log_level=log_level)

    print("Scanning the repository...")
    files = scan_repo(context)

    print(f"\n--\nTotal files selected in repo: {len(files)}\n--\n")

    # Confirm with user the files detected look good
    get_code_insights(files, True)
    confirm = input("\n\nBased on this overview, do you want to proceed with slicing this repo? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborting the slicing process.")
        return
    
    # Prepare output directory
    clean(repo_path)
    os.makedirs(f"{repo_path}/.llm", exist_ok=True)

    '''
    team = AgentTeam(10)


    '''

    # Loop over the files
    # 1- Summarize the file as a whole
    # 2- Slice each file in logical chunks and summarize each chunk
    # 3 - Store the results in the output directory
    '''
    ------------------------------------------
    Steps:
    5- Create a queue of 10 AI agents that will parallel process the chunks and store the results
    '''

def clean(repo_path: str):
    """
    Clean up the local output directory after processing.
    """
    print("Cleaning up output directory...")
    os.system(f"rm -rf {repo_path}/.llm")
    print("Directory cleaned up.")

def main():
    parser = argparse.ArgumentParser(description="Code Sushi: Slice and organize your code repo for LLMs.")
    subparsers = parser.add_subparsers(dest="command",required=True)

    # Add 'dry-run' command
    dry_run_parser = subparsers.add_parser("dry-run", help="Simulate the slicing process without modifying the repo.")
    dry_run_parser.set_defaults(func=dry_run)

    # Add 'upload' command
    upload_parser = subparsers.add_parser("upload", help="Process the repo and upload the results.")
    upload_parser.set_defaults(func=upload)

    # Add 'slice' command
    slice_parser = subparsers.add_parser("slice", help="Slice the repo into chunks for processing.")
    slice_parser.add_argument("--path", required=True, help="Path to the repository to process.")
    slice_parser.add_argument("--log", type=int, default=1, help="Log level (0-3).")

    slice_parser.set_defaults(func=slice)

    # Add 'clean' command
    clean_parser = subparsers.add_parser("clean", help="Clean up the repo after processing.")
    clean_parser.set_defaults(func=clean)
    
    # Parse and execute the appropriate command
    args = parser.parse_args()

    if args.command == "slice":
        args.func(args.path, args.log)
    else:
        args.func()

if __name__ == "__main__":
    main()
