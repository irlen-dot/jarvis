from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional


class ToolType(Enum):
    COMMAND_PROMPT = "command_prompt"
    FILE_WRITER = "file_writer"

@dataclass
class ToolResult:
    """Container for tool execution results"""
    success: bool
    message: str
    data: Optional[Any] = None