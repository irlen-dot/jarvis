import subprocess
import os
import time
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

class UnityProjectCreator:
    def __init__(self):
        self.unity_exe = os.getenv("UNITY_PATH")
        self.projects_path = os.getenv("UNITY_PROJECT_PATH")
        
        if not self.unity_exe or not self.projects_path:
            raise ValueError("Unity path or projects path not found in environment variables")

    def _wait_for_process(self, process, timeout=600) -> bool:
        """
        Wait for Unity process to complete with timeout.
        
        Args:
            process: Subprocess object
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if process completed successfully
        """
        start_time = time.time()
        
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.terminate()
                raise TimeoutError("Unity process took too long")
                
            time.sleep(5)  # Check every 5 seconds
        
        return_code = process.poll()
        if return_code != 0:
            raise subprocess.CalledProcessError(
                return_code, 
                "Unity project creation", 
                output=process.stdout, 
                stderr=process.stderr
            )
        
        return True

    def create_project(self, project_name: str, project_path: str | None = None) -> str:
        """
        Create a Unity project at the specified path.
        
        Args:
            project_name: Name of the project
            project_path: Optional custom path for the project
            
        Returns:
            str: Full path to the created project
        """
        final_path = os.path.join(project_path or self.projects_path, project_name)
        
        command = [
            self.unity_exe,
            "-createProject", final_path,
            "-quit"
        ]
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self._wait_for_process(process)
            return final_path
            
        except (subprocess.CalledProcessError, TimeoutError) as e:
            raise RuntimeError(f"Failed to create Unity project: {str(e)}")

@tool
def create_unity_project(project_name: str, project_path: str | None = None) -> str:
    """
    Tool to create a Unity project.
    
    Args:
        project_name: Name of the project
        project_path: Optional custom path for the project
        
    Returns:
        str: Path to the created project
    """
    creator = UnityProjectCreator()
    return creator.create_project(project_name, project_path)