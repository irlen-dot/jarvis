from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI


class BaseController:
    def __init__(self, llm_selector_class, prompt_text=None, agent=None):
        llm_selector = llm_selector_class()
        self.llm: ChatOpenAI | ChatAnthropic = llm_selector.get_model()
        self.prompt_text = prompt_text
        self.agent = agent
