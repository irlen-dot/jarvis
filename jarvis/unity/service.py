import subprocess
from jarvis.git.service import create_and_push_repo
from dotenv import load_dotenv
import os
import time
from langchain.tools import tool

load_dotenv()

def _get_unity_path() -> str:
    unity_exe = os.getenv("UNITY_PATH")
    return unity_exe

def _get_unity_projects_path() -> str:
    unity_projects_path = os.getenv("UNITY_PROJECT_PATH")
    return unity_projects_path

@tool
def create_unity_project(project_name: str, project_path = None):
    """This tool creates a unity project and returns the path of the project"""
    print(f"Unity project with the name '{project_name}' is being created...")

    unity_projects_path = _get_unity_projects_path()
    unity_exe = _get_unity_path()
    print(f"Starting to create Unity project: {project_name}")
    if project_path == None:
        project_path = unity_projects_path
    project_path = os.path.join(project_path, project_name)
    print(f"Full project path: {project_path}")
    command = [
        unity_exe,
        "-createProject", project_path,
        "-quit"
    ]

    print(f"Running command: {' '.join(command)}")

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Wait for the process to complete
        wait_for_unity_process(process)
        print("Unity project creation completed.")
        # Now create and push the repository
        # print("Creating and pushing repository...")
        # create_and_push_repo(project_path, project_name)
        # print("Repository creation and push completed.")
    except subprocess.CalledProcessError as e:
        print("Failed to create Unity project.")
        print("Error:", e)
        print("Error output:", e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    print("create_project function completed.")
    return project_path

def wait_for_unity_process(process, timeout=600):
        start_time = time.time()

        print("Waiting for Unity to finish creating project files...")
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.terminate()
                print("Timeout: Unity process took too long.")
                return False

            print("Unity is still working...")
            time.sleep(5)  # Check every 5 seconds

        return_code = process.poll()
        if return_code == 0:
            print("Unity process completed successfully.")
            return True
        else:
            print(f"Unity process failed with return code {return_code}")
            return False


# ===============================================================================
# ===============================================================================


class UnityService:
    def __init__(self):
        self.unity_exe = os.getenv("UNITY_PATH")
        self.unity_projects_path = os.getenv("UNITY_PROJECT_PATH")
        print(f"Unity executable path: {self.unity_exe}")
        print(f"Unity projects path: {self.unity_projects_path}")

    def create_project(self, project_name: str, project_path = None):
        print(f"Starting to create Unity project: {project_name}")
        if project_path == None:
            project_path = self.unity_projects_path
        project_path = os.path.join(project_path, project_name)
        print(f"Full project path: {project_path}")

        command = [
            self.unity_exe,
            "-createProject", project_path,
            "-quit"
        ]

        print(f"Running command: {' '.join(command)}")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for the process to complete
            self.wait_for_unity_process(process)

            print("Unity project creation completed.")

            # Now create and push the repository
            print("Creating and pushing repository...")
            create_and_push_repo(project_path, project_name)
            print("Repository creation and push completed.")
        except subprocess.CalledProcessError as e:
            print("Failed to create Unity project.")
            print("Error:", e)
            print("Error output:", e.stderr)
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

        print("create_project function completed.")

    def wait_for_unity_process(self, process, timeout=600):
        start_time = time.time()

        print("Waiting for Unity to finish creating project files...")
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.terminate()
                print("Timeout: Unity process took too long.")
                return False

            print("Unity is still working...")
            time.sleep(5)  # Check every 5 seconds

        return_code = process.poll()
        if return_code == 0:
            print("Unity process completed successfully.")
            return True
        else:
            print(f"Unity process failed with return code {return_code}")
            return False