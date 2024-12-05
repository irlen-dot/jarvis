import msvcrt
import os
import pdb
import sys
import argparse
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
    """Get a single keypress from terminal."""
    key = msvcrt.getch()
    if key == b"\xe0":  # Special key prefix
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

    def create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Code generation and directory information utility"
        )

        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Show both current working directory and script location",
        )

        parser.add_argument(
            "-i",
            "--index",
            help="It indexes all folders and files of the project. So, you that you can have access to the code",
        )

        parser.add_argument(
            "--init-project",
            help="Init a project in Jarvis DB, to mantain a chat history",
        )

        parser.add_argument(
            "--writecode",
            type=str,
            metavar="STRING",
            help="LLM prompt for code generation",
        )

        parser.add_argument(
            "-p", "--prompt", type=str, metavar="STRING", help="Basic LLM prompt"
        )

        return parser

    def show_directory_info(self) -> None:
        print(f"Current working directory: {self.original_working_dir}")
        print(f"Script location: {Path(__file__).parent.resolve()}")

    def select_project_type(self) -> str:
        selected = 0
        while True:
            os.system("cls")
            print("\nSelect project type (↑↓ to move, Enter to select):\n")

            for i, proj_type in enumerate(self.project_types):
                if i == selected:
                    print(f" > {proj_type} <")
                else:
                    print(f"   {proj_type}  ")

            key = get_key()
            if key == "up" and selected > 0:
                selected -= 1
            elif key == "down" and selected < len(self.project_types) - 1:
                selected += 1
            elif key == "\r":  # Enter key
                return self.project_types[selected]

    async def process_args(self, args: argparse.Namespace) -> int:
        if args.all:
            self.show_directory_info()

        if args.index:
            index_controller = IndexController()
            index_controller.start_indexing(str(self.original_working_dir))

        if args.init_project:
            project_type = self.select_project_type()
            self.project_controller.init_project(str(self.original_working_dir))

        if args.writecode:
            print(f"Working directory: {self.original_working_dir}")
            await self.code_controller.manage_input(
                args.writecode, self.original_working_dir
            )

        if args.prompt:
            self.main_controller.manage_input(
                args.prompt, str(self.original_working_dir)
            )

        return 0


async def bootstrap() -> int:
    setup_python_path()
    cli = CodeGenCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    return await cli.process_args(args)


def main() -> int:
    try:
        return asyncio.run(bootstrap())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
