from typing import List
from collections import deque

class Agent:
    def __init__(self, files: List[str]):
        self.files = deque(files)
    
    def start_work(self):
        """
        Start processing the files.
        """
        while self.files:
            file = self.files.popleft()
            self.process_file(file)
    
    def process_file(self, file: str):
        """
        Process a single file.
        """
        pass
        # Read & parse the file
        # Use LLM to extract functions or logical blocks
        # Store the results in the output directory
        # Return the results

        #- each will then summarize the file as whole and in parallel get it chunked up
        #- once chunked up, it will queue it up for processing
