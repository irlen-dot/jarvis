from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

from .model_selector import BaseModelSelector

class ConversationalModelSelector(BaseModelSelector):
    def __init__(self):
        super().__init__("CONVERSATIONAL_MODEL_TYPE", "CONVERSATIONAL_MODEL")
    
    def _get_gpt_model(self):
        return ChatOpenAI(
            model_name=self.model,
            temperature=0.8,
            max_tokens=100
        )
    
    def _get_claude_model(self):
        return ChatAnthropic(
            model=self.model,
            temperature=0.8,
            max_tokens=100
        )