from jarvis.helper.base_controller import BaseController
from jarvis.music.controller import MusicController
from jarvis.project_template.controller import ProjectTempController
from .helper.models.coding_model import CodingModelSelector
from .helper.models.conversation_model import ConversationalModelSelector
from .helper.models.internal_model import InternalModelSelector
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.schema.output_parser import StrOutputParser


class MainController(BaseController):
    def __init__(self):
        super().__init__(
            InternalModelSelector,
            """
        The input is related to:
        'create a project template',
        'download music',
        'turn on music'.

        the output should be: 'coding' or 'music'

        examples:
        Input - 'flutter project named my_project' Output - 'coding',
        Input - 'python Hello_World and push to git' - 'coding',
        Input - 'https://www.youtube.com/watch?v=YG3EhWlBaoI into folder rap' Output - 'music',
        Input - 'Turn on lo/fi' Output - 'music'

        The input is: {input}
        """,
        )
        self.project_temp_controller = ProjectTempController()
        self.music_controller = MusicController()

    def manage_input(self, input, current_path=None):
        self.current_path = current_path
        prompt = PromptTemplate.from_template(self.prompt_text)
        chain = (
            prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(lambda x: self._manage_output(x, input))
        )
        print("Filtering by project_temp, load_music, turn_music....")
        chain.invoke({"input": input})

    def _manage_output(self, content: str, input: str):
        print(f"The output of filtering: {content}")
        if "coding" in content:
            self.project_temp_controller.manage_input(input, self.current_path)
        elif "music" in content:
            self.music_controller.manage_input(input)
        else:
            raise ValueError(
                'The question could not be determined neither as "contents" neither as "coding"'
            )
