import os
from langchain_core.tools import tool
from jarvis.git.types import CreateRepoInput
from jarvis.helper.cmd_prompt import run_command, change_dir
from jarvis.git.gitignores import unity_gitignore, python_gitignore

def create_gitignore(project_type: str):
    """Creates appropriate .gitignore file based on project type"""
    if 'unity' in project_type.lower():
        with open(".gitignore", "w") as f:
            f.write(unity_gitignore.strip())
        print("Created .gitignore file for Unity project")
    elif 'python' in project_type.lower():
        with open(".gitignore", "w") as f:
            f.write(python_gitignore.strip())
        print("Created .gitignore file for Python project")

@tool(args_schema=CreateRepoInput)
def create_and_push_repo(path: str, repo_name: str, project_type: str):
    """Creates a github repository and pushes all the commits"""
    print('Repository creation has started...')
    print(f"The path is: {path}")
    print(f"The project type is: {project_type}")
    
    if not os.path.isdir(path):
        print(f"Error: The directory {path} does not exist or is not accessible.")
        return
    
    with change_dir(path):
        print("--- Starting repository creation process ---")
    

        # Initialize git repository
        if not run_command("git init",):
            print("Error: Failed to initialize git repository")
            return
        
        # Create gitignore
        create_gitignore(project_type)
        
        # Add all files
        if not run_command("git add ."):
            print("Error: Failed to add files to git")
            return
        
        # Create initial commit - using double quotes to avoid quote escaping issues
        if not run_command('git commit -m "Initial commit"'):
            print("Error: Failed to create initial commit")
            return
        
        # Create and push to GitHub repository
        create_repo_cmd = f'gh repo create "{repo_name}" --private --source=. --push'
        if not run_command(create_repo_cmd):
            print("Error: Failed to create GitHub repository. Make sure GitHub CLI is installed and configured.")
            return
        
        print("Repository successfully created and pushed to GitHub!")
        print("--- Finished repository creation process ---")