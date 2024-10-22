# Jarvis - Your AI Computer Assistant

Created by the Almaty Guys. Fully open source. Created, so that I can optimize the process of finishing my university assignments.

**IMPORTANT NOTE**: The project is still in the stage of development. High probability to move to the microservice architecture and use Rust to manage the everything in terms of the computer and python for the AI part.

**Another important note**: It is only on windows for now

Jarvis is a powerful chatbot that automates a variety of tasks on your computer, from creating new projects to managing files and even pushing them to GitHub. With Jarvis, you can simplify your workflow and boost productivity by delegating repetitive tasks to an intelligent assistant.

## Features

- **Project Management**: 
  - Creates new projects on your local machine.
  - Organizes files and folders as needed for your project.

- **System Control**: 
  - Can restart or turn off the computer as commanded.

- **File and Folder Management**: 
  - Automates file and folder organization.
  - Renames, deletes, or moves files to desired locations.

- **GitHub Integration**: 
  - Pushes all projects to GitHub with minimal setup.
  - Can automate commit messages and handle multiple repositories.

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/jarvis.git

2. Install python

https://apps.microsoft.com/detail/9nrwmjp3717k?hl=en-us&gl=US

3. Install Poetry
https://python-poetry.org/docs/#installing-with-pipx


4. Install gh for communicating with github

*with scoop*:
   ```bash
scoop install gh 
```

*or choco*:
```bash
choco install gh
```
5. Navigate to the project and run these commands

```bash
poetry env use python
poetry shell
poetry install
python -m jarvis