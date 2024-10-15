from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

load_dotenv()

class BaseModelSelector:
    '''The BaseModelSelector class is an abstract base class designed to be inherited by other classes. 
    It provides a framework for selecting and managing different AI models based on environment variables.
    Works with Claude and GBT for now.
    


    ```python
    #You inherit from the BaseModelSelector
    class CodingModelSelector(BaseModelSelector):
        def __init__(self):
            super().__init__("MODEL_TYPE_ENV", "MODEL_ENV")

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

    coding_selector = CodingModelSelector()
    coding_model = coding_selector.get_model()
    print(f"Coding model: {coding_model.__class__.__name__}")
    ```

    '''

    # 
    def __init__(self, model_type_env, model_env):
        self.model_type = os.getenv(model_type_env, "gpt").lower()
        self.model = os.getenv(model_env, "gpt-3.5-turbo").lower()
        
    def get_model(self) -> ChatOpenAI | ChatAnthropic:
        if self.model_type == "gpt":
            return self._get_gpt_model()
        elif self.model_type == "claude":
            return self._get_claude_model()
        else:
            raise ValueError(f"Invalid model type: {self.model_type}. Must be 'gpt' or 'claude'.")
    
    def _get_gpt_model(self) -> ChatOpenAI:
        return ChatOpenAI(
            model_name=self.model_type,
            temperature=0.7,
            max_tokens=150
        )
    
    def _get_claude_model(self) -> ChatAnthropic:
        return ChatAnthropic(
            model=self.model_type,
            temperature=0.7,
            max_tokens=150
        )
