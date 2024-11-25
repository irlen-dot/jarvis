from pathlib import Path
from typing import Union, Optional
from langchain.tools import tool


@tool
def write_file(
    content: str, file_path: Union[str, Path], create_dirs: Optional[bool] = True
) -> bool:
    """
    Write content to a file at the specified path, replacing any existing content.
    This operation will overwrite the entire file with new content.

    Args:
        content: Content to write to the file
        file_path: Path where the file should be created
        create_dirs: If True, create parent directories if they don't exist

    Returns:
        bool: True if write was successful, False otherwise
    """
    try:
        # Convert string path to Path object
        path = Path(file_path)

        # Create parent directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        path.write_text(content, encoding="utf-8")

        return True

    except Exception as e:
        print(f"Error writing file: {str(e)}")
        return False


@tool
def append_file(
    content: str, file_path: Union[str, Path], create_dirs: Optional[bool] = True
) -> bool:
    """
    Append content to the end of a file. If the file doesn't exist, it will be created.

    Args:
        content: Content to append to the file
        file_path: Path of the file
        create_dirs: If True, create parent directories if they don't exist

    Returns:
        bool: True if append was successful, False otherwise
    """
    try:
        path = Path(file_path)

        # Create parent directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        # Append the content (creates file if it doesn't exist)
        with open(path, "a", encoding="utf-8") as file:
            file.write(content)

        return True

    except Exception as e:
        print(f"Error appending to file: {str(e)}")
        return False


@tool
def insert_line_into_file(
    content: str,
    file_path: Union[str, Path],
    line_number: int,
    create_dirs: Optional[bool] = True,
) -> bool:
    """
    Insert content at a specific line number in the file. If the line number is greater
    than the file length, the content will be appended to the end of the file.
    Line numbers start at 1.

    Args:
        content: Content to insert
        file_path: Path of the file
        line_number: The line number where content should be inserted (1-based indexing)
        create_dirs: If True, create parent directories if they don't exist

    Returns:
        bool: True if insertion was successful, False otherwise
    """
    try:
        path = Path(file_path)

        # Create parent directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not path.exists():
            path.touch()

        # Read existing lines
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Ensure content ends with a newline if it doesn't already
        if not content.endswith("\n"):
            content += "\n"

        # Handle line number beyond file length
        if line_number > len(lines) + 1:
            line_number = len(lines) + 1

        # Insert the content at the specified line
        if line_number <= 1:
            lines.insert(0, content)
        else:
            lines.insert(line_number - 1, content)

        # Write the modified content back to the file
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        return True

    except Exception as e:
        print(f"Error inserting line: {str(e)}")
        return False


@tool
def read_file(file_path):
    """
    Read content from a file at the specified path and mark each line with a line number.

    Args:
        file_path: Path of the file to read

    Returns:
        str: Content of the file with line numbers if successful
        str: Error message if reading fails
    """
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            # Add line numbers to each line
            numbered_lines = [
                f"Line[{i+1}] {line.rstrip()}" for i, line in enumerate(lines)
            ]
            return "\n".join(numbered_lines)
    except FileNotFoundError:
        return "Error: File not found"
    except Exception as e:
        return f"Error: {str(e)}"
