from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from jarvis.helper.base_controller import BaseController
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

class ToolType(Enum):
    COMMAND_PROMPT = "command_prompt"
    FILE_WRITER = "file_writer"

@dataclass
class ToolResult:
    """Container for tool execution results"""
    success: bool
    message: str
    data: Optional[Any] = None

class CodeGenToolManager:
    """Manages the available coding tools and their execution"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {
            ToolType.COMMAND_PROMPT.value: execute_command,
            ToolType.FILE_WRITER.value: write_file
        }
        
        self.tool_descriptions = {
            ToolType.COMMAND_PROMPT.value: "Execute commands in the command prompt",
            ToolType.FILE_WRITER.value: "Write code or content to files"
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
        
        # Create base prompt
        base_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an agent responsible for writing code. 
            You have these tools available:
            
            {self.tool_manager.get_tool_descriptions()}
            
            Follow these guidelines:
            1. Analyze user requests carefully to determine required tools
            2. Execute tools in the correct order
            3. Provide clear feedback about actions taken
            4. Handle errors gracefully
            5. Ask for clarification if the request is ambiguous"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Initialize model and agent
        super().__init__(CodingModelSelector)
        self.llm = self.get_llm()
        
        # Create agent with tools
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            prompt=base_prompt,
            tools=self.tool_manager.get_available_tools()
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tool_manager.get_available_tools(),
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def manage_input(self, input: str) -> Dict[str, Any]:
        """Process user input and execute appropriate tools"""
        try:
            # Execute agent with input
            result = await self.agent_executor.ainvoke(
                {
                    "input": input,
                    "chat_history": []  # Can be extended to maintain chat history
                }
            )
            
            return {
                "success": True,
                "message": "Tools executed successfully",
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing tools: {str(e)}",
                "error": str(e)
            }
    
    async def _execute_tool(self, tool_type: ToolType, **kwargs) -> ToolResult:
        """Execute a specific tool"""
        tool = self.tool_manager.tools.get(tool_type.value)
        if not tool:
            return ToolResult(
                success=False,
                message=f"Tool {tool_type.value} not found"
            )
        
        try:
            result = await tool.ainvoke(**kwargs)
            return ToolResult(
                success=True,
                message="Tool executed successfully",
                data=result
            )
        except Exception as e:
            return ToolResult(
                success=False,
                message=f"Tool execution failed: {str(e)}"
            )