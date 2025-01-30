from google.cloud import storage
import os
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor
from code_sushi.context import Context, LogLevel
from dotenv import load_dotenv
import time

load_dotenv()

class GoogleCloudStorage:
    def __init__(self, context: Context, bucket_name: Optional[str] = None):
        self.client = storage.Client(
            project=os.getenv('SUSHI_GCP_PROJECT_ID'),
        )
        self.context = context
        self.max_workers = context.blob_storage_concurrent_limit

        if not bucket_name:
            bucket_name = os.getenv('SUSHI_GCP_BUCKET_NAME')
        self.bucket = self.client.bucket(bucket_name)

        self.success_count = 0
        self.failure_count = 0

    def upload_file(self, source_path: str, destination_path: str):
        """
        Uploads a file to the bucket.
        """

        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(source_path)
            self.success_count += 1
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"File {source_path} uploaded to {destination_path}.")
        except Exception as e:
            self.failure_count += 1
            print(f"Error uploading file: {e}")
            raise e
    
    def bulk_upload(self, source_dir: str, destination_dir: str):
        """
        Uploads all files from a directory to the bucket in parallel.
        """
        start = time.time()
        if self.context.is_log_level(LogLevel.DEBUG):
            print(f"Uploading files from {source_dir} with {self.max_workers} threads to GCP.")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    dest_path = os.path.relpath(file_path, source_dir)
                    dest_path = os.path.join(destination_dir, dest_path)

                    if os.path.isfile(file_path):
                        executor.submit(self.upload_file, file_path, dest_path)

        if self.context.is_log_level(LogLevel.DEBUG):   
            runtime = time.time() - start
            print(f"All files uploaded in {runtime:.2f} seconds.")
        
        print(f"Success: {self.success_count}. Failed: {self.failure_count}")

    def download_file(self, source_path: str, destination: str):
        """
        Downloads a file from the bucket to the destination.
        """
        try:
            blob = self.bucket.blob(source_path)
            blob.download_to_filename(destination)

            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Blob {source_path} downloaded to {destination}.")
        except Exception as e:
            print(f"Error in GCP.download_file(): {e}")
            raise e

    def read_file(self, blob_name: str):
        """
        Read the contents of a file from the bucket into memory.
        """
        try:

            if "@" in blob_name:
                blob_name = blob_name.replace("@", ".functions/").rsplit('.', 1)[0]

            if not blob_name.endswith(".md"):
                blob_name += ".md"

            blob = self.bucket.blob(blob_name)
            return str(blob.download_as_string())
        except Exception as e:
            if self.context.is_log_level(LogLevel.DEBUG):
                print(f"Error in GCP.read_file(): {e}")
            raise e

    def delete_file(self, blob_name: str):
        """
        Delete a file from the bucket.
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()

            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Blob {blob_name} deleted.")
        except Exception as e:
            print(f"Error in GCP.delete_file(): {e}")
            raise e

    def list_files(self):
        blobs = self.bucket.list_blobs()
        return [blob.name for blob in blobs]

    def read_many_files(self, blob_names: List[str]) -> List[str]:
        """
        Read the contents of multiple files from the bucket into memory.
        """
        contents = []
        start = time.time()
        
        try:
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Starting to read {len(blob_names)} files from storage into memory")

            def read_blob(blob_name):
                try:
                    if not blob_name:
                        return

                    contents.append(self.read_file(blob_name))
                except Exception as e:
                    if self.context.is_log_level(LogLevel.DEBUG):
                        print(f"Error reading file {blob_name}: {e}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                executor.map(read_blob, blob_names)
            
            if self.context.is_log_level(LogLevel.DEBUG):
                runtime = time.time() - start
                print(f"{len(contents)} files successfully read in {runtime:.2f} seconds.")
            
            return contents
        except Exception as e:
            print(f"Error in gcp.read_many_files(): {e}")
            return []
