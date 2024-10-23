from jarvis.git.service import create_and_push_repo
from jarvis.helper.base_controller import BaseController
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

from jarvis.python.service import create_python_project
from jarvis.unity.service import create_unity_project


class ProjectTempController(BaseController):
    def __init__(self):
        super().__init__(CodingModelSelector)
        tools = [create_unity_project, create_python_project, create_and_push_repo]
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant that creates projects and sets up git repositories.

            Process:
            1. When a user requests a project creation, use either python_project or unity_project tool.
            2. After creating the project, if the user mentioned anything about git/github/repository, use the git_repo tool with the returned project path.
            3. Always return the final results to the user.

            Example flow:
            - If user says "Create a python project called test with git", you should:
              1. Call python_project tool
              2. Take the returned path
              3. Call git_repo tool with that path
            - If user just says "Create a unity project called game", you should:
              1. Only call unity_project tool""",
                ),
                # ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def manage_input(self, input: str):
        self.agent_executor.invoke({"input": input})

