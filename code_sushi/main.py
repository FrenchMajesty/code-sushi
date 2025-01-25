
import argparse
from .core import scan_repo 
from .context import Context

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

def slice(repo_path: str):
    """
    Slice the repository into chunks for processing.
    """
    print("Slicing the repository...")
    context = Context(repo_path=repo_path)
    filepaths = scan_repo(context)
    print(len(filepaths), ' files found in that repository')

    '''
    ------------------------------------------
    Steps:
    1- Get the list of files in the repository.
    2- Filter out the ones in .gitignore
    3- Confirm with user list looks good before proceeding
    4- Slice the list into chunks
    5- Create a queue of 10 AI agents that will parallel process the chunks and store the results
    '''

def clean():
    """
    Clean up the repository after processing.
    """
    print("Cleaning up the repository...")

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
    slice_parser.set_defaults(func=slice)

    # Add 'clean' command
    clean_parser = subparsers.add_parser("clean", help="Clean up the repo after processing.")
    clean_parser.set_defaults(func=clean)
    
    # Parse and execute the appropriate command
    args = parser.parse_args()

    if args.command == "slice":
        args.func(args.path)
    else:
        args.func()

if __name__ == "__main__":
    main()
