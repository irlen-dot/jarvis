import subprocess
from jarvis.git.service import create_and_push_repo
from jarvis.helper.cmd_prompt import run_command
from jarvis.project_template.types import Project_Type_Name
from dotenv import load_dotenv
import os
import time

load_dotenv()

class UnityService:
    def __init__(self):
        self.unity_exe = os.getenv("UNITY_PATH")
        self.unity_projects_path = os.getenv("UNITY_PROJECT_PATH")
        print(f"Unity executable path: {self.unity_exe}")
        print(f"Unity projects path: {self.unity_projects_path}")

    def create_project(self, project_name: str):
        print(f"Starting to create Unity project: {project_name}")
        project_path = os.path.join(self.unity_projects_path, project_name)
        print(f"Full project path: {project_path}")

        # Create Unity project
        log_file = os.path.join(project_path, "unity_create_log.txt")
        command = [
            self.unity_exe,
            "-batchmode",
            "-createProject", project_path,
            "-logFile", log_file,
            "-quit"
        ]

        print(f"Running command: {' '.join(command)}")

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for the process to complete
            self.wait_for_unity_process(process, log_file)
            
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

    def wait_for_unity_process(self, process, log_file, timeout=600):
        start_time = time.time()
        last_log_size = 0
        no_change_time = time.time()

        print("Waiting for Unity to finish creating project files...")
        while process.poll() is None:
            if time.time() - start_time > timeout:
                process.terminate()
                print("Timeout: Unity process took too long.")
                return False

            if os.path.exists(log_file):
                current_size = os.path.getsize(log_file)
                if current_size > last_log_size:
                    print("Unity is still working...")
                    last_log_size = current_size
                    no_change_time = time.time()
                elif time.time() - no_change_time > 30:  # No change for 30 seconds
                    print("No progress detected for 30 seconds. Assuming completion.")
                    break

            time.sleep(5)  # Check every 5 seconds

        # Read and print the log file
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                log_content = f.read()
            print("Unity log output:")
            print(log_content)

        return_code = process.poll()
        if return_code == 0:
            print("Unity process completed successfully.")
            return True
        else:
            print(f"Unity process failed with return code {return_code}")
            return False

    # def wait_for_unity_project(self, project_path, timeout=300):
    #     print("Waiting for Unity to finish creating project files...")
    #     start_time = time.time()
    #     while time.time() - start_time < timeout:
    #         if self.is_unity_project_ready(project_path):
    #             print("Unity project files are ready.")
    #             return True
    #         time.sleep(5)  # Check every 5 seconds
    #     print("Timeout waiting for Unity project files.")
    #     return False

    # def is_unity_project_ready(self, project_path):
    #     Check for essential Unity project files/folders
    #     essential_items = ['Assets', 'ProjectSettings', 'Packages']
    #     return all(os.path.exists(os.path.join(project_path, item)) for item in essential_items)
    

    
        