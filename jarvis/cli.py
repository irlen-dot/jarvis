import os
import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

# Ensure project root is in Python path
def setup_python_path() -> None:
    """Add project root to Python path if needed."""
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

from jarvis.codegen.controller import CodeGenController

class CodeGenCLI:
    """CLI interface for the code generation system."""
    
    def __init__(self):
        """Initialize CLI with working directory and controller."""
        self.original_working_dir = Path.cwd()
        self.controller = CodeGenController()
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser.
        
        Returns:
            Configured argument parser
        """
        parser = argparse.ArgumentParser(
            description='Code generation and directory information utility'
        )
        
        parser.add_argument(
            '-a', '--all',
            action='store_true',
            help='Show both current working directory and script location'
        )
        
        parser.add_argument(
            '--writecode',
            type=str,
            metavar='STRING',
            help='LLM prompt for code generation'
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
        if args.all:
            self.show_directory_info()
        
        if args.writecode:
            print(f"Working directory: {self.original_working_dir}")
            await self.controller.manage_input(
                args.writecode,
                str(self.original_working_dir)
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