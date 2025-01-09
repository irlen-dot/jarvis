# index_controller.py
import click
from jarvis.helper.cmd_prompt import change_dir, run_command
from jarvis.index_project.service import IndexService


class IndexController:
    def __init__(self):
        self.index_service = IndexService()

    def clear_collection(self, path: str) -> None:
        """Handle collection clearing request."""
        try:
            result = self.index_service.clear_collection(path)
            if result["success"]:
                click.echo(
                    f"Successfully deleted collection: {result['collection_name']}"
                )
            else:
                click.echo(
                    f"Warning: Collection {result['collection_name']} was not found in database"
                )
        except Exception as e:
            click.echo(f"Error clearing collection: {str(e)}")
            raise

    def start_indexing(self, path: str) -> None:
        """Handle project indexing request."""
        try:
            result = self.index_service.main_indexing(path)

            if result["success"]:
                click.echo(f"Successfully indexed project:")
                click.echo(f"- Collection name: {result['collection_name']}")
                click.echo(f"- Chunks processed: {result['chunks_processed']}")
            else:
                click.echo(f"Error during indexing: {result['error']}")

        except Exception as e:
            click.echo(f"Error during indexing: {str(e)}")
            raise

    def index_added_files(self, path: str):
        """Indexes files that are added to the project"""
        with change_dir(path):
            (_, added_files) = run_command(f"git ls-files --others --exclude-standard")
            if added_files:
                added_files_array = [
                    f for f in added_files.strip().split("\n") if f.endswith(".cs")
                ]

                print(added_files_array)
                if added_files_array[0]:  # Check if array is not just an empty string
                    click.echo(f"Found {len(added_files_array)} new files to index")
                else:
                    click.echo("No new files found to index")
            else:
                added_files_array = []
                click.echo("No new files found to index")
