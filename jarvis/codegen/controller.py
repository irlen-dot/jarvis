import json
from pathlib import Path
import pdb
from typing import List, Dict, Any
from jarvis.codegen.prompts import get_code_gen_agent_prompt
from jarvis.codegen.service import (
    append_file,
    read_file,
    overwrite_file,
    insert_line,
    overwrite_lines,
)
from jarvis.codegen.types import ToolResult, ToolType
from jarvis.helper.base_controller import BaseController
from jarvis.helper.cmd_prompt import run_command
from jarvis.helper.db import Database, Role, Session
from jarvis.helper.embedding import EmbeddingService
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage

from jarvis.helper.vector_db import VectorDB


class CodeGenToolManager:
    """Manages the available coding tools and their execution"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            ToolType.COMMAND_PROMPT.value: run_command,
            ToolType.FILE_OVERWRITER.value: overwrite_file,
            ToolType.LINES_OVERWRITER.value: overwrite_lines,
            ToolType.FILE_READER.value: read_file,
            ToolType.FILE_APPENDER.value: append_file,
            ToolType.FILE_INSERT_LINE.value: insert_line,
        }

        self.tool_descriptions = {
            ToolType.COMMAND_PROMPT.value: "Execute commands in the command prompt",
            ToolType.FILE_OVERWRITER.value: "It overwrites the whole file.",
            ToolType.FILE_READER.value: "Read the content of the file",
            ToolType.FILE_APPENDER.value: "Write code or content to files. It adds content to the end of the file.",
            ToolType.LINES_OVERWRITER.value: "It overwrites specific lines.",
            ToolType.FILE_INSERT_LINE.value: "Write code or content to files. It adds content at a specific line.",
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


class CodeGenController(BaseController):
    """Controller for code generation and tool execution"""

    def __init__(self):
        self.tool_manager = CodeGenToolManager()
        tools = self.tool_manager.get_tool_descriptions()
        super().__init__(
            llm_selector_class=CodingModelSelector,
            prompt_text=get_code_gen_agent_prompt(tools),
        )

        # Create base prompt
        base_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.prompt_text),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.agent = create_tool_calling_agent(
            llm=self.llm,
            prompt=base_prompt,
            tools=self.tool_manager.get_available_tools(),
        )

        self.embedding = EmbeddingService()
        self.db = Database()

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tool_manager.get_available_tools(),
            verbose=True,
            handle_parsing_errors=True,
        )

    def get_file_indexes(self, input: str, path: str):
        collection = self.db.get_collection_by_path(path=path)
        print(f"The collection name: {collection.name}")
        pdb.set_trace()
        vector_store = VectorDB(collection_name=collection.name)
        embeddings = self.embedding.embed_query(input)
        # TODO Clean this part of the code
        return vector_store.search(embeddings)[0].get("text")

    async def manage_input(self, input: str, path: Path) -> Dict[str, Any]:
        """Process user input and execute appropriate tools"""
        path = str(path)
        messages = self.db.get_messages_by_sessions_path(path)
        indexed_files = self.get_file_indexes(input=input, path=path)
        print(indexed_files)

        # Convert to LangChain message objects
        formatted_messages = []
        if messages is not None:
            formatted_messages = [
                (
                    HumanMessage(content=msg.content)
                    if msg.role == Role.HUMAN
                    else AIMessage(content=msg.content)
                )
                for msg in messages
            ]

        agent_input = input + f"\n\n The available files: {indexed_files}"

        try:
            # Execute agent with input
            result = await self.agent_executor.ainvoke(
                {
                    "input": agent_input,
                    "chat_history": formatted_messages,
                }
            )

            output: str = result["output"]
            session = self.db.find_session_by_path(path)

            self.db.add_message(session_id=session.id, content=input, role=Role.HUMAN)
            self.db.add_message(session_id=session.id, content=output, role=Role.AI)

            return {
                "success": True,
                "message": "Tools executed successfully",
                "result": output,
            }

        except Exception as e:
            print(f"Error executing agent: {str(e)}")  # Added for debugging
            return {
                "success": False,
                "message": f"Error executing tools: {str(e)}",
                "error": str(e),
            }

    async def _execute_tool(self, tool_type: ToolType, **kwargs) -> ToolResult:
        """Execute a specific tool"""
        tool = self.tool_manager.tools.get(tool_type.value)
        if not tool:
            return ToolResult(
                success=False, message=f"Tool {tool_type.value} not found"
            )

        try:
            result = await tool.ainvoke(**kwargs)
            return ToolResult(
                success=True, message="Tool executed successfully", data=result
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Tool execution failed: {str(e)}")
