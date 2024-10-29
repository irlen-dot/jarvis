import json
from jarvis.git.service import create_and_push_repo
from jarvis.helper.base_controller import BaseController
from jarvis.helper.db import Database, Role
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

from jarvis.project_template.prompt import project_templ_controller_prompt
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
                    project_templ_controller_prompt,
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        self.db = Database()

    # TODO move the session db logic to here.
    def manage_input(self, input: str):
        output = self.agent_executor.invoke({"input": input})
        print(f"The raw output of the agent: {output}")
        result = json.load(output)
        self.db.add_message(session_id=result['session_id'], content=result['content'], role=Role.AI)
        print(f"The agent executor output: {result}")

