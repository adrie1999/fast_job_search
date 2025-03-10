import os
from typing import Optional


def get_most_recent_file(base_path: str) -> Optional[str]:
    """
    Get the most recent file from a specified directory and its subdirectories based on the last modification time.

    Args:
        base_path (str): The directory path to search for the files.

    Returns:
        Optional[str]: The full path to the most recent file, or None if no files are found.
    """
    most_recent_file = None
    most_recent_time = 0

    # Walk through the directory and all its subdirectories
    for root, dirs, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_mod_time = os.path.getmtime(file_path)

            # If the current file is more recent, update the most recent file
            if file_mod_time > most_recent_time:
                most_recent_time = file_mod_time
                most_recent_file = file_path

    return most_recent_file
