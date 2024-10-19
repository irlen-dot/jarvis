import subprocess
from jarvis.git.service import create_and_push_repo
from jarvis.helper.cmd_prompt import run_command
from jarvis.project_template.types import Project_Type_Name
from dotenv import load_dotenv
import os

load_dotenv()

class UnityService:
    def __init__(self):
        self.unity_exe = os.getenv("UNITY_PATH")
        self.unity_projects_path = os.getenv("UNITY_PROJECT_PATH") 

    def create_project(self, project_name: str):
    
        
        project_path = self.unity_projects_path + f'\{project_name}'
        command = [self.unity_exe, "-createProject", project_path]
        run_command(command)
        create_and_push_repo(project_path)

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Unity project created successfully.")
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Failed to create Unity project.")
            print("Error:", e)
            print("Output:", e.output)
    

    
        