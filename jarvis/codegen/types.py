from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional


class ToolType(Enum):
    COMMAND_PROMPT = "command_prompt"
    FILE_OVERWRITER = "file_overwriter"
    FILE_READER = "file_reader"
    FILE_APPENDER = "file_appender"
    FILE_INSERT_LINE = "file_insert_line"
    LINES_OVERWRITER = "line_overwriter"


@dataclass
class ToolResult:
    """Container for tool execution results"""

    success: bool
    message: str
    data: Optional[Any] = None
