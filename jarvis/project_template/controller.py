import json
from typing import Any, Dict
from jarvis.git.service import create_and_push_repo
from jarvis.helper.base_controller import BaseController
from jarvis.helper.db import Database, Role
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
import pdb
from jarvis.helper.string_to_dict import string_to_dict
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

    def manage_input(self, input: str, current_path) -> Dict[str, Any]:
        invoke_query = {"input": input}
        if current_path:
            invoke_query["current_path"] = current_path

        # Parse output from string to Dictionary
        result = self.agent_executor.invoke(invoke_query)

        output = string_to_dict(result["output"])

        # Store the Human input and AI output into a session,
        # related to this specific project
        session = self.db.create_session(path=output.get("path_to_project"))
        self.db.add_message(session_id=session.id, content=input, role=Role.HUMAN)
        self.db.add_message(
            session_id=session.id, content=output.get("content"), role=Role.AI
        )

        return output
