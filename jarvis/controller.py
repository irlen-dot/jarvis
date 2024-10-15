from .helper.models.coding_model import CodingModelSelector
from .helper.models.conversation_model import ConversationalModelSelector
from .helper.models.internal_model import InternalModelSelector
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.schema.output_parser import StrOutputParser

class Controller:


    def __init__(self):
        coding_model_selector = CodingModelSelector()
        conversation_model_selector = ConversationalModelSelector()
        internal_model_selector = InternalModelSelector()
        self.coding_model = coding_model_selector.get_model()
        self.conversation_model = conversation_model_selector.get_model()
        self.internal_model = internal_model_selector.get_model()

    def manage_input(self, input):
        prompt_text = """The input is either related to the computer or it is just a conversation.
Give an output as 'coding' if it is related to the computer or 'conversation' if it is just a conversation.
'Create a folder with flutter', 'Turn on the music', 'Restart' - coding.
'Who is George Washington?', 'How are you doing?', 'Wassup' - conversation.
                                      
the input is: {input}"""
        prompt = PromptTemplate.from_template(prompt_text)
        chain = (
            prompt | self.internal_model | StrOutputParser() | RunnableLambda(self._manage_convers_or_coding)
        )
        chain.invoke({ 'input': input })
        

    def _manage_convers_or_coding(self, content):
        print(content)
        if 'coding' in content:
            print('I am coding')
        elif 'conversation' in content:
            print('I am conversation')
        else:
            raise ValueError('The question could not be determined neither as "contents" neither as "coding"')