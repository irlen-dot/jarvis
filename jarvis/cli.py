import click
import msvcrt
import os
import sys
import asyncio
from pathlib import Path
from jarvis.index_project.controller import IndexController
from jarvis.main_controller import MainController
from jarvis.project_template.controller import ProjectTempController
from jarvis.codegen.controller import CodeGenController


def setup_python_path() -> None:
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))


def get_key() -> str:
    key = msvcrt.getch()
    if key == b"\xe0":
        key = msvcrt.getch()
        return {b"H": "up", b"P": "down"}.get(key, None)
    return key.decode("utf-8")


class CodeGenCLI:
    def __init__(self):
        self.original_working_dir = Path.cwd()
        self.code_controller = CodeGenController()
        self.main_controller = MainController()
        self.project_controller = ProjectTempController()
        self.project_types = ["unity", "python", "nodejs"]

    def show_directory_info(self) -> None:
        click.echo(f"Current working directory: {self.original_working_dir}")
        click.echo(f"Script location: {Path(__file__).parent.resolve()}")

    def select_project_type(self) -> str:
        selected = 0
        while True:
            os.system("cls")
            click.echo("\nSelect project type (↑↓ to move, Enter to select):\n")

            for i, proj_type in enumerate(self.project_types):
                if i == selected:
                    click.echo(f" > {proj_type} <")
                else:
                    click.echo(f"   {proj_type}  ")

            key = get_key()
            if key == "up" and selected > 0:
                selected -= 1
            elif key == "down" and selected < len(self.project_types) - 1:
                selected += 1
            elif key == "\r":
                return self.project_types[selected]

    async def process_command(
        self, show_all: bool, index: str, init_project: str, writecode: str, prompt: str
    ) -> int:
        if show_all:
            self.show_directory_info()

        if index:
            index_controller = IndexController()
            index_controller.start_indexing(str(self.original_working_dir))

        if init_project:
            project_type = self.select_project_type()
            self.project_controller.init_project(str(self.original_working_dir))

        if writecode:
            click.echo(f"Working directory: {self.original_working_dir}")
            await self.code_controller.manage_input(
                writecode, self.original_working_dir
            )

        if prompt:
            self.main_controller.manage_input(prompt, str(self.original_working_dir))

        return 0


@click.command()
@click.option(
    "-a",
    "--all",
    is_flag=True,
    help="Show both current working directory and script location",
)
@click.option(
    "-i", "--index", help="Index all folders and files of the project for code access"
)
@click.option(
    "--init-project", help="Init a project in Jarvis DB to maintain chat history"
)
@click.option("--writecode", help="LLM prompt for code generation")
@click.option("-p", "--prompt", help="Basic LLM prompt")
def main(all, index, init_project, writecode, prompt):
    """Code generation and directory information utility"""
    try:
        setup_python_path()
        cli = CodeGenCLI()
        return asyncio.run(
            cli.process_command(all, index, init_project, writecode, prompt)
        )
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        return 1
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
