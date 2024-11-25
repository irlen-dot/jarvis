from pathlib import Path
from typing import Union, Optional, List
from langchain.tools import tool


@tool
def overwrite_lines(
    content: str,
    file_path: Union[str, Path],
    start_line: int,
    end_line: int,
    create_dirs: Optional[bool] = True,
) -> bool:
    """
    Overwrite lines in a file between start_line and end_line (inclusive) with new content.
    If line numbers exceed file length, file will be extended with empty lines.

    Args:
        content: Content to write
        file_path: Path of the file
        start_line: First line to overwrite (1-based indexing)
        end_line: Last line to overwrite (1-based indexing)
        create_dirs: If True, create parent directories if they don't exist

    Returns:
        bool: True if overwrite was successful, False otherwise
    """
    try:
        print("Invoking overwrite_lines...")
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            path.touch()

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Split content into lines
        content_lines = content.splitlines(keepends=True)

        while len(lines) < end_line:
            lines.append("\n")

        # Replace the specified range with new content lines
        lines[start_line - 1 : end_line] = content_lines

        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)
        print("Invoked overwrite_lines.")
        return True
    except Exception as e:
        print(f"Error overwriting lines: {str(e)}")
        return False


@tool
def overwrite_file(
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
        path = Path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
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
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error appending to file: {str(e)}")
        return False


@tool
def insert_line(
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
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.touch()

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if not content.endswith("\n"):
            content += "\n"

        if line_number > len(lines) + 1:
            line_number = len(lines) + 1

        if line_number <= 1:
            lines.insert(0, content)
        else:
            lines.insert(line_number - 1, content)

        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        return True
    except Exception as e:
        print(f"Error inserting line: {str(e)}")
        return False


@tool
def delete_lines(
    file_path: Union[str, Path], line_numbers: Union[int, List[int], range]
) -> bool:
    """
    Delete specific lines from a file. Line numbers start at 1.

    Args:
        file_path: Path of the file
        line_numbers: Single line number, list of line numbers, or range of lines to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            print("Error: File not found")
            return False

        # Convert single line number to list
        if isinstance(line_numbers, int):
            line_numbers = [line_numbers]
        elif isinstance(line_numbers, range):
            line_numbers = list(line_numbers)

        # Convert to 0-based indexing and sort in reverse
        line_indices = sorted([i - 1 for i in line_numbers], reverse=True)

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Remove lines from the end to avoid index shifting
        for index in line_indices:
            if 0 <= index < len(lines):
                lines.pop(index)

        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)

        return True
    except Exception as e:
        print(f"Error deleting lines: {str(e)}")
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
            numbered_lines = [
                f"Line[{i+1}] {line.rstrip()}" for i, line in enumerate(lines)
            ]
            return "\n".join(numbered_lines)
    except FileNotFoundError:
        return "Error: File not found"
    except Exception as e:
        return f"Error: {str(e)}"
