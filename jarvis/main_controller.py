from jarvis.helper.base_controller import BaseController
from .helper.models.coding_model import CodingModelSelector
from .helper.models.conversation_model import ConversationalModelSelector
from .helper.models.internal_model import InternalModelSelector
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.schema.output_parser import StrOutputParser
from .project_template.controller import ProjectTemplateController

class MainController(BaseController):
    def __init__(self):
        super().__init__(InternalModelSelector, """
        The input is related to:
        'create a project template',
        'download music',
        'turn on music'.

        the output should be: 'create_project', 'load_music', 'turn_on_music'

        examples:
        Input - 'flutter project named my_project' Output - 'create_project',
        Input - 'https://www.youtube.com/watch?v=YG3EhWlBaoI' Output - 'load_music',
        Input - 'Turn on lo/fi' Output - 'turn_on_music'

        The input is: {input}
        """)
        self.project_temp_controller = ProjectTemplateController()

    def manage_input(self, input): 
        prompt = PromptTemplate.from_template(self.prompt_text)
        chain = (
            prompt | self.model | StrOutputParser() | RunnableLambda(lambda x: self._manage_output(x, input))
        )
        print("Filtering by project_temp, load_music, turn_music....")
        chain.invoke({ 'input': input })


    def _manage_output(self, content: str, input: str):
        print(f"The output of filtering: {content}")
        if 'create_project' in content:
            self.project_temp_controller.manage_input(input)
        elif 'load_music' in content:
            print('I am load_music')
        elif 'turn_on_music' in content:
            print('I am turn_on_music')
        else:
            raise ValueError('The question could not be determined neither as "contents" neither as "coding"')
        