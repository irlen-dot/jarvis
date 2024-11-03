from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional


class ToolType(Enum):
    COMMAND_PROMPT = "command_prompt"
    FILE_MODIFIER = "file_modifier"
    FILE_READER = "file_reader"


@dataclass
class ToolResult:
    """Container for tool execution results"""

    success: bool
    message: str
    data: Optional[Any] = None
