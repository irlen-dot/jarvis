from pathlib import Path
from typing import Any, Union, Optional, Dict
from langchain.tools import tool
import json

from jarvis.helper.string_to_dict import string_to_dict


def chunk_content(content: str, chunk_size: int = 8000) -> list[str]:
    """Split content into manageable chunks."""
    return [content[i : i + chunk_size] for i in range(0, len(content), chunk_size)]


@tool
def write_file(input) -> Dict[str, Any]:
    """
    Write content to a file at the specified path with support for large files.

    Args:
        input: {
            content: Content to write to the file,
            file_path: Path where the file should be created,
            mode: Optional write mode ('w' for write, 'a' for append)
        }
    Returns:
        dict: Status of the operation including success flag and message
    """
    try:
        output = string_to_dict(input) if isinstance(input, str) else input
        content = output.get("content", "")
        file_path = output.get("file_path")
        mode = output.get("mode", "w")

        if not content or not file_path:
            return {
                "success": False,
                "message": "Both content and file_path are required",
            }

        path = Path(file_path)

        # Handle large content by writing in chunks
        if len(content) > 8000:  # Adjust threshold as needed
            chunks = chunk_content(content)

            # Write first chunk with 'w' mode to create/overwrite file
            path.write_text(chunks[0], encoding="utf-8")

            # Append remaining chunks
            with open(path, "a", encoding="utf-8") as f:
                for chunk in chunks[1:]:
                    f.write(chunk)
        else:
            # For smaller content, write directly
            path.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "message": f"Successfully wrote content to {file_path}",
            "bytes_written": path.stat().st_size,
        }

    except Exception as e:
        return {"success": False, "message": f"Error writing file: {str(e)}"}


@tool
def read_file(file_path: str) -> Dict[str, Any]:
    """
    Read content from a file at the specified path with improved error handling.

    Args:
        file_path: Path of the file to read

    Returns:
        dict: Contains success flag, message, and content if successful
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {
                "success": False,
                "message": f"File not found: {file_path}",
                "content": None,
            }

        content = path.read_text(encoding="utf-8")
        return {
            "success": True,
            "message": "File read successfully",
            "content": content,
            "bytes_read": path.stat().st_size,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error reading file: {str(e)}",
            "content": None,
        }
