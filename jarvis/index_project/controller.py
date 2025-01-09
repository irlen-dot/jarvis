# index_controller.py
import click
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
            result = self.index_service.start_indexing(path)

            if result["success"]:
                click.echo(f"Successfully indexed project:")
                click.echo(f"- Collection name: {result['collection_name']}")
                click.echo(f"- Chunks processed: {result['chunks_processed']}")
            else:
                click.echo(f"Error during indexing: {result['error']}")

        except Exception as e:
            click.echo(f"Error during indexing: {str(e)}")
            raise

    # def index_added_files(self, ):
