import json
from pathlib import Path
from typing import List, Dict, Any
from enum import Enum
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from jarvis.helper.base_controller import BaseController
from jarvis.helper.db import Database
from jarvis.helper.models.music_model import MusicModelSelector
from jarvis.music.service import youtube_to_mp3


class ToolType(Enum):
    """Types of music tools available"""
    YOUTUBE_TO_MP3 = "youtube_to_mp3"
    PLAYLIST_MANAGER = "playlist_manager"
    MUSIC_INFO = "music_info"


class MusicToolManager:
    """Manages the available music tools and their execution"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            ToolType.YOUTUBE_TO_MP3.value: youtube_to_mp3,
        }

        self.tool_descriptions = {
            ToolType.YOUTUBE_TO_MP3.value: "Downloads YouTube videos as MP3 files",
        }

    def get_available_tools(self) -> List[BaseTool]:
        """Get list of available tools"""
        return list(self.tools.values())

    def get_tool_descriptions(self) -> str:
        """Get formatted tool descriptions for prompt"""
        return "\n".join(
            f"{i+1}. {name}: {desc}"
            for i, (name, desc) in enumerate(self.tool_descriptions.items())
        )


def get_music_agent_prompt(tools: str) -> str:
    """Returns the prompt for the music agent"""
    return f"""You are a music management assistant that helps users with various music-related tasks.
    
Available tools:
{tools}

For each request:
1. Understand what the user wants to do with their music
2. Choose the appropriate tool(s) for the task
3. Execute the tools in the correct order
4. Return the direct path or result from the tool execution

Always ensure proper error handling and validation of inputs.
"""


class MusicController(BaseController):
    """Controller for music operations and tool execution"""

    def __init__(self):
        self.tool_manager = MusicToolManager()
        tools = self.tool_manager.get_tool_descriptions()
        super().__init__(
            llm_selector_class=MusicModelSelector,
            prompt_text=get_music_agent_prompt(tools),
            agent=None
        )
        self.db = Database()

        # Create base prompt
        base_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_text),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Set the agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            prompt=base_prompt,
            tools=self.tool_manager.get_available_tools(),
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tool_manager.get_available_tools(),
            verbose=True,
            handle_parsing_errors=True,
        )

    async def manage_input(self, input: str) -> str:
        """
        Process user input and execute appropriate music tools.
        Returns the direct result/path from the tool execution.
        """

        try:
            result = await self.agent_executor.ainvoke(
                {
                    "input": input,
                    "chat_history": [],
                }
            )

            session = self.db.get_latest_session_by_path(path)
            self.db.add_message(session_id=session.id, content=result["output"])

            return result["output"]  # Direct output from the tool

        except Exception as e:
            raise Exception(f"Error performing music operation: {str(e)}")

    async def _execute_tool(self, tool_type: ToolType, **kwargs) -> Any:
        """Execute a specific music tool and return its direct result"""
        tool = self.tool_manager.tools.get(tool_type.value)
        if not tool:
            raise Exception(f"Tool {tool_type.value} not found")

        try:
            return await tool.ainvoke(**kwargs)  # Direct result from the tool
        except Exception as e:
            raise Exception(f"Tool execution failed: {str(e)}")
