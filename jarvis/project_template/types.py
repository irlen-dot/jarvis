from typing import Optional

from pydantic import BaseModel, Field

class Project_Type_Name(BaseModel):
    """You are creating a project. What is the project language or framework? And what is the name of the project?
    this class tells the chat model what exactly should it output"""

    project_name: str = Field(description="What is the name of the project")
    project_type: str = Field(description="The language or framework of the project")