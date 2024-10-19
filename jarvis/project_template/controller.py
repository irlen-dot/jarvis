from jarvis.helper.base_controller import BaseController
from jarvis.helper.models.coding_model import CodingModelSelector
from jarvis.helper.models.internal_model import InternalModelSelector
from jarvis.project_template.types import Project_Type_Name
# from jarvis.project_template.tools import project_temp_tools
from langchain_core.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from langgraph.prebuilt import create_react_agent

from jarvis.unity.service import UnityService 

class ProjectTemplateController(BaseController):
    def __init__(self):
        super().__init__(CodingModelSelector, prompt_text="""
The input contains the information about the language or framework of the project (flutter, python, node.js, unity)
and the name of the project (my_project, Jarvis, Rain in blood)

the output should identify the name and the type.
                         
Examples:
'create python hello_world': type - 'python' name - 'hello_world'
'flutter Lucem Hospital': type - 'flutter' name - 'Lucem Hospital'
                         
Input: {input}
""")
        self.unity_service = UnityService()

    def manage_input(self, input: str):
        structured_model = self.model.with_structured_output(Project_Type_Name)
        prompt = PromptTemplate.from_template(self.prompt_text)
        chain = prompt | structured_model | RunnableLambda(self._manage_output)  

        print("Getting info about the langauge, framework, name of the project...")

        print("The input of the shit is: " + input)

        chain.invoke({ 'input': input })

    def _manage_output(self, output: Project_Type_Name):
        if 'unity' in output.project_type:
            self.unity_service.create_project(output.project_name)