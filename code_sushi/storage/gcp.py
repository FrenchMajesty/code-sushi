from google.cloud import storage
import os
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from code_sushi.context import Context, LogLevel
import time

class GoogleCloudStorage:
    def __init__(self, context: Context, bucket_name: Optional[str] = None, concurrent_threads: int = 20):
        self.client = storage.Client(
            project=os.getenv('GCP_PROJECT_ID'),
        )
        self.context = context
        self.max_workers = concurrent_threads

        if not bucket_name:
            bucket_name = os.getenv('GCP_BUCKET_NAME')
        self.bucket = self.client.bucket(bucket_name)

    def upload_file(self, source_path: str, destination_path: str):
        """
        Uploads a file to the bucket.
        """

        try:
            blob = self.bucket.blob(destination_path)
            blob.upload_from_filename(source_path)

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"File {source_path} uploaded to {destination_path}.")
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise e
    
    def bulk_upload(self, source_dir: str, destination_dir: str):
        """
        Uploads all files from a directory to the bucket in parallel.
        """
        start = time.time()
        if self.context.log_level.value >= LogLevel.DEBUG.value:
            print(f"Uploading files from {source_dir} with {self.max_workers} threads.")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for root, _, files in os.walk(source_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    dest_path = os.path.relpath(file_path, source_dir)
                    dest_path = os.path.join(destination_dir, dest_path)

                    if os.path.isfile(file_path):
                        executor.submit(self.upload_file, file_path, dest_path)
            
        if self.context.log_level.value >= LogLevel.DEBUG.value:
            runtime = time.time() - start
            print(f"All files uploaded in {runtime:.2f} seconds.")

    def download_file(self, source_path: str, destination: str):
        """
        Downloads a file from the bucket to the destination.
        """
        try:
            blob = self.bucket.blob(source_path)
            blob.download_to_filename(destination)

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Blob {source_path} downloaded to {destination}.")
        except Exception as e:
            print(f"Error downloading file: {e}")
            raise e

    def read_file(self, blob_name: str):
        """
        Read the contents of a file from the bucket into memory.
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.download_as_string()
        except Exception as e:
            print(f"Error reading file: {e}")
            raise e

    def delete_file(self, blob_name: str):
        """
        Delete a file from the bucket.
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()

            if self.context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Blob {blob_name} deleted.")
        except Exception as e:
            print(f"Error deleting file: {e}")
            raise e

    def list_files(self):
        blobs = self.bucket.list_blobs()
        return [blob.name for blob in blobs]
