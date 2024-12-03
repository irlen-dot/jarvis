import os
import pdb
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

from jarvis.helper.vector_db import VectorDB
from jarvis.index_project.controller import IndexController
from jarvis.main_controller import MainController
from jarvis.project_template.controller import ProjectTempController


from jarvis.codegen.controller import CodeGenController


# Ensure project root is in Python path
def setup_python_path() -> None:
    """Add project root to Python path if needed."""
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))


class CodeGenCLI:
    """CLI interface for the code generation system."""

    def __init__(self):
        """Initialize CLI with working directory and controller."""
        self.original_working_dir = Path.cwd()
        self.code_controller = CodeGenController()
        self.main_controller = MainController()
        self.project_controller = ProjectTempController()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser.

        Returns:
            Configured argument parser
        """
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
        """Display current directory information."""
        print(f"Current working directory: {self.original_working_dir}")
        print(f"Script location: {Path(__file__).parent.resolve()}")

    async def process_args(self, args: argparse.Namespace) -> int:
        """Process parsed command line arguments.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code (0 for success)
        """
        # pdb.set_trace()
        print(args.init_project)

        if args.all:
            self.show_directory_info()

        if args.index:
            index_controller = IndexController()
            index_controller.start_indexing(str(self.original_working_dir))

        if args.init_project:
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
    """Initialize and run the CLI application.

    Returns:
        Exit code (0 for success)
    """
    setup_python_path()

    cli = CodeGenCLI()
    parser = cli.create_parser()
    args = parser.parse_args()

    return await cli.process_args(args)


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success)
    """
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
