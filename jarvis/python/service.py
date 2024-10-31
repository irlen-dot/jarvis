import subprocess
import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from langchain_core.tools import tool
from jarvis.helper.cmd_prompt import run_command
from jarvis.helper.db import Database, Role

@dataclass
class ProjectSettings:
    """Data class to hold project configuration settings"""
    name: str
    base_path: Optional[str] = None
    python_version: str = "python"

    @property
    def full_path(self) -> Path:
        """Get the complete project path"""
        base = self.base_path or os.getenv("PYTHON_PROJECT_PATH")
        if not base:
            raise ValueError("Project path not provided and PYTHON_PROJECT_PATH not set")
        return Path(base) / self.name

class VSCodeConfigurator:
    """Handles VS Code configuration settings"""
    
    @staticmethod
    def setup_interpreter(project_path: Path, interpreter_path: str) -> None:
        """Configure VS Code Python interpreter settings"""
        vscode_dir = project_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        settings_file = vscode_dir / "settings.json"
        settings = {}
        
        if settings_file.exists():
            with settings_file.open('r') as f:
                settings = json.load(f)
        
        settings.update({
            "python.defaultInterpreterPath": interpreter_path,
            "python.pythonPath": interpreter_path
        })
        
        with settings_file.open('w') as f:
            json.dump(settings, f, indent=4)
        
        print(f"VS Code interpreter set to: {interpreter_path}")

class PoetryEnvironment:
    """Manages Poetry-related operations"""
    
    @staticmethod
    def verify_installation() -> None:
        """Check if Poetry is installed"""
        try:
            subprocess.run(
                ["poetry", "--version"],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError:
            raise EnvironmentError("Poetry is not installed. Please install Poetry and try again.")

    @staticmethod
    def create_project(project_path: Path) -> None:
        """Create a new Poetry project"""
        subprocess.run(["poetry", "new", str(project_path)], check=True)

    @staticmethod
    def setup_environment(python_version: str) -> str:
        """Setup Poetry virtual environment and return interpreter path"""
        commands = [
            ["poetry", "env", "use", python_version],
            ["poetry", "shell"]
        ]
        
        for cmd in commands:
            subprocess.run(cmd, check=True)
        
        result = subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

class PythonProjectManager:
    """Main class for managing Python project creation and setup"""
    
    def __init__(self):
        PoetryEnvironment.verify_installation()
        self.db = Database()
        
    def create_project(self, settings: ProjectSettings) -> Path:
        """Create and configure a new Python project"""
        project_path = settings.full_path
        original_dir = Path.cwd()
        session = self.db.create_session(str(project_path))
        try:
            # Create and setup project
            PoetryEnvironment.create_project(project_path)
            os.chdir(project_path)
            
            # Setup virtual environment
            interpreter_path = PoetryEnvironment.setup_environment(settings.python_version)
            
            if interpreter_path:
                VSCodeConfigurator.setup_interpreter(project_path, interpreter_path)
            else:
                print("Warning: Failed to get interpreter path. VS Code settings not configured.")
            
            # Launch VS Code
            # TODO Decomment
            # run_command(f"code {str(project_path)}")
            
            self.db.add_message(session_id=session.id, content=f"create a python project in path {settings.full_path}", role=Role.HUMAN)

            return project_path, session.id
            
        finally:
            os.chdir(original_dir)


@tool
def create_python_project(project_name: str, project_path: str = None) -> str:
    """Create a new Python project with Poetry and VS Code configuration
    
    Args:
        project_name: Name of the project to create
        project_path: Optional base path for project creation
    
    Returns:
        1. String representation of the created project's path
        2. The ID of the session the project is attached to
    """
    print(f"Creating Python project: '{project_name}'...")
    
    settings = ProjectSettings(
        name=project_name,
        base_path=project_path
    )
    
    manager = PythonProjectManager()
    created_path, session_id = manager.create_project(settings)
    
    return str(created_path), session_id 