# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
# from langchain.tools import BaseTool, StructuredTool, tool

class CreateRepoInput(BaseModel):
    path: str = Field(description="The path of the project. Which is given by the previous tools") 
    repo_name: str = Field(description="The name of the repository. Given by user's initial input") 
    project_type: str = Field(description="The type of the project. For example, 'python' 'unity' 'flutter'")