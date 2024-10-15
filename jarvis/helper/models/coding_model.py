from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from jarvis.helper.models.model_selector import BaseModelSelector

class CodingModelSelector(BaseModelSelector):
    def __init__(self):
        super().__init__("CODING_MODEL_TYPE", "CODING_MODEL")
    
    def _get_gpt_model(self):
        return ChatOpenAI(
            model_name=self.model,
            temperature=0.2,
            max_tokens=300
        )
    
    def _get_claude_model(self):
        return ChatAnthropic(
            model=self.model,
            temperature=0.2,
            max_tokens=300
        )