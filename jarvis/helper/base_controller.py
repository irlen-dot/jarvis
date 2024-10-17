from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class BaseController:
    def __init__(self, model_selector_class, prompt_text):
        model_selector = model_selector_class()
        self.model: ChatOpenAI | ChatAnthropic = model_selector.get_model()
        self.prompt_text = prompt_text