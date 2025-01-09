# index_service.py
import os
import random
from typing import Dict, List, Optional
from yaml import safe_load
from jarvis.helper.db import Database
from jarvis.helper.embedding import EmbeddingService
from jarvis.helper.vector_db import VectorDB
from jarvis.index_project.agent import IndexCodeAgent
from pymilvus import utility


class IndexService:
    DIMENSIONS = 1536
    DOCUMENT_SEPARATOR = "===============CUT==============="

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index_code_agent = IndexCodeAgent()
        self.db_service = Database()

    def clear_collection(self, path: str) -> None:
        """Clear a collection and its associated documents from both vector database and metadata storage.

        Args:
            path (str): The file system path of the project whose collection should be cleared

        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the deletion was successful
                - collection_name (str): Name of the cleared collection

        Raises:
            Exception: If no collection exists for the given path
        """

        existing_collection = self.db_service.get_collection_by_path(path)
        if not existing_collection:
            raise Exception(f"No collection found for project at path: {path}")

        collection_name = existing_collection.name
        vector_db = VectorDB(collection_name=collection_name, dim=self.DIMENSIONS)

        vector_db.clear_collection()
        result = self.db_service.delete_collection_by_path(path)
        return {"success": result, "collection_name": collection_name}

    def get_projects_config(self, path: str) -> Dict[str, any]:
        """Read and parse Jarvis.yaml configuration."""
        config_path = os.path.join(path, "Jarvis.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return safe_load(file.read())
        except FileNotFoundError:
            raise FileNotFoundError(
                "Jarvis.yaml is missing. Run 'jarvis --init .' command."
            )

    def _generate_collection_name(self, path: str) -> str:
        """Generate a unique collection name based on parent folder."""
        path_parts = os.path.normpath(path).split(os.sep)
        base_name = path_parts[-2] if len(path_parts) >= 2 else path_parts[-1]

        collection_name = base_name.replace(" ", "_").replace("-", "_")
        temp_db = VectorDB(collection_name=collection_name, dim=self.DIMENSIONS)

        if utility.has_collection(collection_name):
            while True:
                random_num = random.randint(1, 999)
                new_name = f"{collection_name}_{random_num}"
                if not utility.has_collection(new_name):
                    return new_name

        return collection_name

    def should_ignore_dir(self, dir_path: str, ignored_directories: List[str]) -> bool:
        """Check if directory should be ignored."""
        dir_name = os.path.basename(dir_path)
        return any(
            ignored.lower() == dir_name.lower() or ignored.lower() in dir_path.lower()
            for ignored in ignored_directories
        )

    def process_file(
        self, path: str, name: str, indexed_doc: str
    ) -> tuple[Optional[str], str]:
        """Process a single file and return its analysis."""
        try:
            content = self._read_file(path, name)
            file_analysis = self.index_code_agent.start_indexing(content)
            abs_path = os.path.abspath(os.path.join(path, name))
            file_analysis = f"{file_analysis}\npath: {abs_path}"
            indexed_doc += f"{file_analysis}\n"
            return file_analysis, indexed_doc
        except Exception as e:
            print(f"Error processing file {name}: {str(e)}")
            return None, indexed_doc

    def _read_file(self, path: str, name: str) -> str:
        """Read file content."""
        file_path = os.path.join(path, name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise IOError(f"Error reading file {name}: {str(e)}")

    def walk_through_project(
        self,
        path: str,
        ignored_directories: List[str],
        included_file_extensions: List[str],
    ) -> str:
        """Walk through project directories and process files."""
        file_count = 0
        indexed_doc = ""
        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d
                for d in dirs
                if not self.should_ignore_dir(
                    os.path.join(root, d), ignored_directories
                )
            ]
            included_files = [
                f
                for f in files
                if any(
                    f.lower().endswith(ext.lower()) for ext in included_file_extensions
                )
            ]

            for file in included_files:
                _, indexed_doc = self.process_file(root, file, indexed_doc)
                file_count += 1
                if file_count % 3 == 0 or file_count % 4 == 0:
                    indexed_doc += f"\n{self.DOCUMENT_SEPARATOR}\n"
        return indexed_doc

    def process_single_file(self, file_path: str) -> Optional[Dict]:
        """Process a single file by its path and return its analysis.

        Args:
            file_path (str): Full path to the file to process

        Returns:
            Optional[Dict]: Dictionary containing the analysis and embeddings if successful,
                          None if processing fails
        """
        try:
            # Extract path and filename
            path = os.path.dirname(file_path)
            name = os.path.basename(file_path)

            # Process the file
            file_analysis, indexed_doc = self.process_file(path, name, "")

            if file_analysis is None:
                return None

            # Create embeddings
            embedded_chunks = self.chunk_and_embed_documents(indexed_doc)

            if not embedded_chunks:
                return None

            return {"analysis": file_analysis, "embedded_chunks": embedded_chunks}

        except Exception as e:
            print(f"Error processing single file {file_path}: {str(e)}")
            return None

    def chunk_and_embed_documents(self, indexed_doc: str) -> List[Dict]:
        """Chunk documents and create embeddings."""
        if not indexed_doc:
            return []

        documents = indexed_doc.split(self.DOCUMENT_SEPARATOR)
        chunks = [doc.strip() for doc in documents if doc.strip()]

        embeddings_input = []
        for chunk in chunks:
            metadata = {}
            path_line = [
                line for line in chunk.split("\n") if line.startswith("path: ")
            ]
            if path_line:
                metadata["path"] = path_line[0].replace("path: ", "")
            embeddings_input.append({"text": chunk, "metadata": metadata})

        return self.embedding_service.embed_chunks(embeddings_input)

    def save_to_vector_db(
        self, embedded_chunks: List[Dict], vector_db: VectorDB
    ) -> None:
        """Save embedded chunks to vector database.

        Takes the embedded chunks (text, embeddings vectors, and file paths) and stores them
        in the vector database for later similarity search and retrieval. The chunks are
        stored with their associated metadata to maintain traceability back to source files.
        """

        texts = [chunk["text"] for chunk in embedded_chunks]
        vectors = [chunk["embedding"] for chunk in embedded_chunks]
        paths = [chunk["metadata"]["path"] for chunk in embedded_chunks]
        vector_db.insert(texts=texts, file_paths=paths, vectors=vectors)

    def save_collection_metadata(self, collection_name: str, base_path: str) -> Dict:
        """Save collection metadata to database."""
        existing_collection = self.db_service.get_collection_by_path(base_path)
        if existing_collection:
            return existing_collection

        return self.db_service.create_project_collection(
            name=collection_name, path=base_path
        )

    def get_collection_metadata(self, path: str) -> Dict:
        """Get collection metadata for a given project path.

        Args:
            path (str): The project path to get metadata for

        Returns:
            Dict: Collection metadata if found, empty dict if not found
        """
        collection = self.db_service.get_collection_by_path(path)
        if collection:
            return {
                "name": collection.name,
                "path": collection.path,
                "created_at": collection.created_at,
            }
        return {}

    def check_collection_exists(self, path: str) -> Dict:
        """
        Check if a collection already exists for this project path.

        Args:
            path (str): The project path to check

        Returns:
            Dict: Information about existing collection or None
        """
        existing_collection = self.db_service.get_collection_by_path(path)
        if existing_collection:
            return {"exists": True, "name": existing_collection.name, "path": path}
        return {"exists": False}

    # TODO: Move this function to the controller
    def main_indexing(self, path: str) -> Dict:
        """Main indexing process."""
        try:
            # First check if collection exists
            collection_check = self.check_collection_exists(path)
            if collection_check["exists"]:
                return {
                    "success": True,
                    "skip_indexing": True,
                    "collection_name": collection_check["name"],
                    "message": f"Collection already exists for this project",
                }

            configs = self.get_projects_config(path)

            ignored_directories = configs.get("ignored-directories", [])
            included_file_extensions = configs.get("included-file-extensions", [])
            starting_directory = configs.get("starting-directory", "")

            full_path = os.path.join(path, starting_directory)

            collection_name = self._generate_collection_name(full_path)
            vector_db = VectorDB(collection_name=collection_name, dim=self.DIMENSIONS)

            indexed_doc = self.walk_through_project(
                full_path, ignored_directories, included_file_extensions
            )
            embedded_chunks = self.chunk_and_embed_documents(indexed_doc)
            self.save_to_vector_db(embedded_chunks, vector_db)
            collection_info = self.save_collection_metadata(collection_name, path)

            return {
                "success": True,
                "skip_indexing": False,
                "collection_name": collection_name,
                "collection_info": collection_info,
                "chunks_processed": len(embedded_chunks),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
