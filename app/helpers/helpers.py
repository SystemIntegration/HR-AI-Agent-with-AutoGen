import re
import hashlib
import json
import os

def extract_category_from_filename(filename: str) -> str:
    """
    Extracts a clean category name from a given filename.

    This function:
    - Removes the file extension.
    - Replaces underscores and hyphens with spaces.
    - Removes numeric digits (e.g., years).
    - Capitalizes each word for readability.

    Args:
        filename (str): The filename to extract the category from.

    Returns:
        str: A cleaned and formatted category name.
    """
    name = filename.rsplit('.', 1)[0]  # remove file extension
    name = re.sub(r'[_\-]+', ' ', name)  # replace underscores/hyphens with spaces
    name = re.sub(r'\d+', '', name)  # remove digits (years etc.)
    return name.strip().title()  # capitalize words (e.g. "Leave Policy")

def compute_hash(content: bytes):
    """
    Computes a SHA-256 hash of the given content.

    Args:
        content (bytes): The content to hash.

    Returns:
        str: The SHA-256 hexadecimal hash of the content.
    """
    return hashlib.sha256(content).hexdigest()

def load_cache(filepath):
    """
    Loads a JSON cache from the specified file path.

    Args:
        filepath (str): The path to the cache file.

    Returns:
        dict: The loaded cache data, or an empty dictionary if the file doesn't exist.
    """
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_cache(data, filepath):
    """
    Saves the given data to a JSON file at the specified file path.

    Creates directories if they do not exist.

    Args:
        data (dict): The data to save.
        filepath (str): The path to the cache file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)