# Quick notice: I thought that it would be better and not that stubid, https://www.youtube.com/watch?v=ouNHbs3Urus, watch this.
# So yeah not THAT STUBID TO separate the agent from controller because well yeah.

from langchain.agents import AgentExecutor, create_tool_calling_agent
from typing import List
from langchain_openai import OpenAI
from pydantic import BaseModel, Field
from jarvis.helper.base_controller import BaseController
from jarvis.helper.models.coding_model import CodingModelSelector
from langchain.output_parsers import JsonOutputToolsParser
from jarvis.index_project.prompt import analyze_code_prompt
from langchain.prompts import PromptTemplate


class CodeComponent(BaseModel):
    name: str = Field(description="Name of the interface or class")
    type: str = Field(description="Whether it's an interface or class")
    description: str = Field(
        description="Detailed description of the component's purpose and functionality"
    )


class CodeAnalysis(BaseModel):
    components: List[CodeComponent] = Field(
        description="List of identified interfaces and classes"
    )


class IndexCodeAgent(BaseController):
    def __init__(self):
        super().__init__(
            llm_selector_class=CodingModelSelector,
            prompt_text=analyze_code_prompt,
        )
        self.model = CodingModelSelector().get_model()
        self.base_prompt = PromptTemplate(
            template=self.prompt_text, input_variables=["code"]
        )

    def start_indexing(self, content: str) -> str:
        prompt = self.base_prompt.invoke({"code": content})
        output = self.model.invoke(prompt)
        print(output.content)
        return output.content
