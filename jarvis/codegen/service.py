import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from langchain.tools import tool

from jarvis.helper.string_to_dict import string_to_dict


def mark_code_lines(content: str, start_num: int = 1) -> str:
    """
    Add line numbers and markers to code content.

    Args:
        content: The source code content
        start_num: Starting line number
    Returns:
        Tuple[str, int]: Marked content and total lines
    """
    lines = content.splitlines()
    max_line_num_width = len(str(start_num + len(lines)))

    marked_lines = []
    for i, line in enumerate(lines, start_num):
        # Create line marker with consistent width
        marker = f"[Line {i:>{max_line_num_width}}]"
        # Preserve indentation by finding leading spaces
        indentation = len(line) - len(line.lstrip())
        # Add marker after indentation
        marked_line = line[:indentation] + marker + " " + line[indentation:]
        marked_lines.append(marked_line)

    return "\n".join(marked_lines)


@tool
def read_code_file(file_path: str) -> Dict[str, Any]:
    """
    Read a code file with metadata about its structure.

    Args:
        file_path: Path to the code file
    Returns:
        dict: File content and metadata
    """
    try:
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")

        # Basic code structure analysis
        lines = content.splitlines()

        return {
            "success": True,
            "content": mark_code_lines(content),
            "total_lines": len(lines),
            "file_path": str(path),
            "exists": True,
        }
    except FileNotFoundError:
        return {
            "success": True,
            "content": "",
            "total_lines": 0,
            "file_path": str(file_path),
            "exists": False,
        }
    except Exception as e:
        return {"success": False, "message": f"Error reading file: {str(e)}"}


def safe_string_to_dict(input_str: Union[str, dict]) -> dict:
    """
    Safely convert string to dictionary, handling various string formats.

    Args:
        input_str: Input string or dictionary
    Returns:
        dict: Parsed dictionary
    """
    if isinstance(input_str, dict):
        return input_str

    try:
        # Try direct JSON parsing first
        return json.loads(input_str)
    except json.JSONDecodeError:
        try:
            # Handle single quotes by replacing with double quotes
            # but preserve escaped single quotes
            processed_str = input_str.replace("\\'", "ESCAPED_QUOTE")
            processed_str = processed_str.replace("'", '"')
            processed_str = processed_str.replace("ESCAPED_QUOTE", "\\'")
            return json.loads(processed_str)
        except json.JSONDecodeError:
            try:
                # Try eval as last resort with basic safety checks
                if any(
                    dangerous in input_str.lower()
                    for dangerous in ["import", "exec", "eval", "os.", "system"]
                ):
                    raise ValueError("Potentially unsafe input")
                return eval(input_str, {"__builtins__": {}}, {})
            except Exception as e:
                raise ValueError(f"Could not parse input string: {str(e)}")


@tool
def modify_code_section(input_dict: str) -> Dict[str, Any]:
    """
    Modify a specific section of code in a file.

    Args:
        input_dict: {
            file_path: Path to the code file,
            start_line: Starting line number (1-based),
            end_line: Ending line number (1-based),
            new_content: New code content,
            action: 'replace', 'insert', or 'append'
        }
    Returns:
        dict: Status of the modification
    """
    try:
        # Parse input safely
        input_data = (
            safe_string_to_dict(input_dict)
            if isinstance(input_dict, str)
            else input_dict
        )

        # Extract parameters
        file_path = input_data.get("file_path")
        new_content = input_data.get("new_content", "")
        action = input_data.get("action", "replace")

        # Process new_content to handle escaped newlines
        if isinstance(new_content, str):
            # Handle triple quotes if present
            if new_content.startswith("'''") and new_content.endswith("'''"):
                new_content = new_content[3:-3]
            elif new_content.startswith('"""') and new_content.endswith('"""'):
                new_content = new_content[3:-3]

            # Decode escaped newlines and other special characters
            new_content = bytes(new_content, "utf-8").decode("unicode_escape")

        if not file_path or new_content is None:
            return {
                "success": False,
                "message": "file_path and new_content are required",
            }

        path = Path(file_path)

        # Read existing content
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        # Ensure all lines end with newline
        lines = [line.rstrip("\n") + "\n" for line in lines]

        # Split new content into lines properly
        new_lines = new_content.splitlines(True)  # Keep the line endings
        if new_lines and not new_content.endswith("\n"):
            new_lines[-1] = new_lines[-1].rstrip("\n") + "\n"

        if action == "replace":
            start_line = input_data.get("start_line")
            end_line = input_data.get("end_line")

            if not (start_line and end_line):
                return {
                    "success": False,
                    "message": "start_line and end_line are required for replace action",
                }

            # Adjust for 0-based indexing while preserving line numbers
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)

            result_lines = lines[:start_idx] + new_lines + lines[end_idx:]

        elif action == "insert":
            start_line = input_data.get("start_line", 1)
            insert_idx = max(0, start_line - 1)
            result_lines = lines[:insert_idx] + new_lines + lines[insert_idx:]

        elif action == "append":
            if lines and not lines[-1].endswith("\n"):
                lines[-1] = lines[-1] + "\n"
            result_lines = lines + new_lines

        else:
            return {"success": False, "message": f"Invalid action: {action}"}

        # Write the modified content
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(result_lines)

        return {
            "success": True,
            "message": f"Successfully modified {file_path}",
            "action": action,
            "total_lines": len(result_lines),
            "modified_line_range": {
                "start": input_data.get("start_line"),
                "end": input_data.get("end_line"),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error modifying code: {str(e)}",
            "details": {
                "file_path": file_path if "file_path" in locals() else None,
                "action": action if "action" in locals() else None,
            },
        }


@tool
def debug_code_section(input_dict: str) -> Dict[str, Any]:
    """
    Analyze and debug a section of code.

    Args:
        input_dict: {
            file_path: Path to the code file,
            start_line: Optional starting line number,
            end_line: Optional ending line number,
            issue_description: Optional description of the issue
        }
    Returns:
        dict: Debug analysis results
    """
    try:
        input_data = (
            string_to_dict(input_dict) if isinstance(input_dict, str) else input_dict
        )

        file_path = input_data.get("file_path")
        start_line = input_data.get("start_line")
        end_line = input_data.get("end_line")
        issue_description = input_data.get("issue_description", "")

        # Read the file content
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Extract relevant section if line numbers provided
        if start_line and end_line:
            code_section = "\n".join(lines[start_line - 1 : end_line])
        else:
            code_section = content

        return {
            "success": True,
            "code_section": code_section,
            "total_lines": len(lines),
            "file_path": str(path),
            "section_start": start_line,
            "section_end": end_line,
            "issue_description": issue_description,
        }

    except Exception as e:
        return {"success": False, "message": f"Error analyzing code: {str(e)}"}
