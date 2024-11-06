import json
import re
from typing import Any, Dict


def string_to_dict(text: str):
    """
    Extracts JSON content from a string that contains JSON markup with triple quotes.

    Args:
        text (str): Input string containing JSON with triple quote markers

    Returns:
        dict: Parsed JSON content

    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    match = text
    if text.startswith("{") == False:
        # Find content between triple quotes and json keyword
        pattern = r"```json\s*(.*?)```"
        match = re.search(pattern, text, re.DOTALL)

    if not match:
        raise ValueError("No JSON content found between triple quotes")

    json_str = match.group(1).strip()

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON content: {str(e)}")


# def string_to_dict(input: str) -> Dict[str, Any]:
#     print(f"The input to the {input}")

#     json_str = extract_json_content(input)

#     return json_str
