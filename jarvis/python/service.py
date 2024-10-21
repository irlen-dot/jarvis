import subprocess
import os
import json
from jarvis.helper.cmd_prompt import run_command

class PythonService():
    def __init__(self):
        self.check_poetry_installation()
    
    def create_project(self, project_name: str, project_path: str = None):
        if project_path is None:
            project_path = os.getenv("PYTHON_PROJECT_PATH")
        project_path = os.path.join(project_path, project_name)
        current_path = os.getcwd()
        
        # Create new project
        subprocess.run(["poetry", "new", str(project_path)], check=True)
        
        # Change to project directory
        os.chdir(project_path)
        
        # Create and activate virtual environment
        subprocess.run(["poetry", "shell"], check=True)
        
        # Get interpreter path
        result = subprocess.run(["poetry", "env", "info", "--path"], capture_output=True, text=True, check=True)
        interpreter_path = result.stdout.strip()
        
        print(f"Interpreter path: {interpreter_path}")
        if interpreter_path:
            self.set_vscode_interpreter(project_path, interpreter_path)
        else:
            print("Failed to get project interpreter path. VS Code interpreter not set.")
        
        # Open VS Code
        subprocess.Popen(["code", project_path])
        
        # Change back to original directory
        os.chdir(current_path)
    
    def check_poetry_installation(self):
        try:
            subprocess.run(["poetry", "--version"], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError:
            raise EnvironmentError("Poetry is not installed. Please install Poetry and try again.")
    
    def set_vscode_interpreter(self, project_path, interpreter_path):
        vscode_settings_dir = os.path.join(project_path, ".vscode")
        os.makedirs(vscode_settings_dir, exist_ok=True)
        
        settings_file = os.path.join(vscode_settings_dir, "settings.json")
        
        settings = {}
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        
        settings["python.defaultInterpreterPath"] = interpreter_path
        settings["python.pythonPath"] = interpreter_path
        
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print(f"VS Code interpreter set to: {interpreter_path}")