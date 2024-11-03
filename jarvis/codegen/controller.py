import json
from pathlib import Path
import pdb
from typing import List, Dict, Any
from jarvis.codegen.prompts import get_code_gen_agent_prompt
from jarvis.codegen.service import (
    modify_code_section,
    read_code_file,
)
from jarvis.codegen.types import ToolResult, ToolType
from jarvis.helper.base_controller import BaseController
from jarvis.helper.cmd_prompt import run_command
from jarvis.helper.db import Database, Session
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.tools import BaseTool
from langchain.agents import (
    AgentExecutor,
    create_tool_calling_agent,
    create_react_agent,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain import hub


class CodeGenToolManager:
    """Manages the available coding tools and their execution"""

    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            ToolType.COMMAND_PROMPT.value: run_command,
            ToolType.FILE_MODIFIER.value: modify_code_section,
            ToolType.FILE_READER.value: read_code_file,
        }

        self.tool_descriptions = {
            ToolType.COMMAND_PROMPT.value: "Execute commands in the command prompt",
            ToolType.FILE_MODIFIER.value: "Modife a section of code in a file",
            ToolType.FILE_READER.value: "Read the content of the file",
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
        print("CodeGenController started to init...")
        self.tool_manager = CodeGenToolManager()
        tools_description = (
            self.tool_manager.get_tool_descriptions()
        )  # Changed variable name for clarity

        # Only pass the expected arguments to super().__init__()
        super().__init__(
            llm_selector_class=CodingModelSelector,
            prompt_text=get_code_gen_agent_prompt(tools_description),
        )

        self.db = Database()

        prompt = hub.pull("hwchase17/react")

        # Pass the actual tool objects, not the description string
        self.agent = create_react_agent(
            llm=self.llm,
            prompt=prompt,
            tools=self.tool_manager.get_available_tools(),  # Use the actual tools list
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tool_manager.get_available_tools(),
            verbose=True,
            handle_parsing_errors=True,
        )
        print("CodeGenController inited...")

    async def manage_input(self, input: str, path: str) -> Dict[str, Any]:
        """Process user input and execute appropriate tools"""

        path = Path(path)

        input = input + f"\n\n The current path of the directory is: {path}"

        try:
            print("Starting to invoke the reAct agent...")
            # Execute agent with input
            result = await self.agent_executor.ainvoke(
                {
                    "input": input,
                    "chat_history": [],  # Can be extended to maintain chat history
                }
            )
            print("Invoked the reAct agent")
            output: str = result["output"]
            json_str = output.split("}")[0] + "}"
            output: Dict[str, Any] = json.loads(json_str)

            session = self.db.get_latest_session_by_path(path)

            self.db.add_message(session_id=session.id, content=output.get("content"))

            return {
                "success": True,
                "message": "Tools executed successfully",
                "result": output,
            }

        except Exception as e:
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
