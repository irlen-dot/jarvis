from langchain_openai import ChatOpenAI
from jarvis.helper.base_controller import BaseController
from jarvis.helper.models.coding_model import CodingModelSelector
from jarvis.helper.models.internal_model import InternalModelSelector
from jarvis.project_template.types import Project_Type_Name
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent

from langgraph.prebuilt import create_react_agent

from jarvis.python.service import create_python_project
from jarvis.unity.service import create_unity_project 


tools = [create_unity_project, create_python_project]

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Make sure to use the python_project tool for creating python project. And the unity_project tool for creating the unity project.",
        ),
        # ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def manage_project_temp_input(input: str):
    agent_executor.invoke({"input": input})


# class ProjectTemplateController(BaseController):
#     def __init__(self):
#         super().__init__(CodingModelSelector, prompt_text="""
# The input contains the information about the language or framework of the project (flutter, python, node.js, unity)
# and the name of the project (my_project, Jarvis, Rain in blood)

# the output should identify the name and the type.
                         
# Examples:
# 'create python hello_world': type - 'python' name - 'hello_world'
# 'flutter Lucem Hospital': type - 'flutter' name - 'Lucem Hospital'
                         
# Input: {input}
# """)
#         self.unity_service = UnityService()

#     def manage_input(self, input: str):
#         structured_model = self.model.with_structured_output(Project_Type_Name)
#         prompt = PromptTemplate.from_template(self.prompt_text)
#         chain = prompt | structured_model | RunnableLambda(self._manage_output)  

#         print("Getting info about the langauge, framework, name of the project...")

#         print("The input of the shit is: " + input)

#         chain.invoke({ 'input': input })

#     def _manage_output(self, output: Project_Type_Name):
#         print(output)
#         if 'unity' in output.project_type:
#             self.unity_service.create_project(output.project_name)