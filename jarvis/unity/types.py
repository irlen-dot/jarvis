
from pydantic import BaseModel, Field


class UnityProjectCreationInput(BaseModel):
    project_name: int = Field(description="The name of the project you want to create")

