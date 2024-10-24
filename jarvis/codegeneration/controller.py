from typing import List
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from jarvis.helper.base_controller import BaseController
from jarvis.helper.cmd_prompt import run_command
from jarvis.helper.models.coding_model import CodingModelSelector

class CodeGenController(BaseController):
    """Controller for managing code generation with LangChain tools."""

    SYSTEM_PROMPT = """
    You are an agent responsible for writing code. You have these tools available:
    1. Create the necessary command prompt commands
    2. Write code to a file

    Your working pipeline has two stages:
    1. You need to run the command the will create the file (the commands are for powershell)
    2. The script
    """

    def __init__(self):
        """Initialize the controller with tools and agent executor."""
        super().__init__(CodingModelSelector, self.SYSTEM_PROMPT)
        
        self.tools = self._setup_tools()
        self.agent_executor = self._create_agent_executor()

    def _setup_tools(self) -> List[BaseTool]:
        """Set up the available tools for the agent.
        
        Returns:
            List of LangChain tools
        """
        # TODO: Add actual tool implementations
        return [run_command]

    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the chat prompt template.
        
        Returns:
            Configured ChatPromptTemplate
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.prompt_text),
            ("human", "{input}"),
            ("assistant", "{agent_scratchpad}")
        ])

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with tools and prompt.
        
        Returns:
            Configured AgentExecutor
        """
        prompt = self._create_prompt()
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True
        )

    async def manage_input(self, input: str) -> dict:
        """Process user input through the agent executor.
        
        Args:
            input: User input string
            
        Returns:
            Dictionary containing execution results
        """
        try:
            result = await self.agent_executor.ainvoke({"input": input})
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }