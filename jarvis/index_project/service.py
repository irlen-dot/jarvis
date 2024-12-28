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
        self.base_path = ""
        self.indexed_doc = ""
        self.collection_name = None
        self.vector_db = None
        self.ignored_directories = []
        self.included_file_extensions = []
        self.current_path = None
        self.current_name = None

    def clear_collection(self, path: str) -> None:
        """Clear a collection and its documents."""
        existing_collection = self.db_service.get_collection_by_path(path)
        if not existing_collection:
            raise Exception(f"No collection found for project at path: {path}")

        self.collection_name = existing_collection.name
        self.vector_db = VectorDB(
            collection_name=self.collection_name, dim=self.DIMENSIONS
        )
        self.vector_db.clear_collection()

        result = self.db_service.delete_collection_by_path(path)
        return {"success": result, "collection_name": self.collection_name}

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

    def should_ignore_dir(self, dir_path: str) -> bool:
        """Check if directory should be ignored."""
        dir_name = os.path.basename(dir_path)
        return any(
            ignored.lower() == dir_name.lower() or ignored.lower() in dir_path.lower()
            for ignored in self.ignored_directories
        )

    def process_file(self) -> Optional[str]:
        """Process a single file and return its analysis."""
        try:
            content = self._read_file()
            file_analysis = self.index_code_agent.start_indexing(content)
            abs_path = os.path.abspath(
                os.path.join(self.current_path, self.current_name)
            )
            file_analysis = f"{file_analysis}\npath: {abs_path}"
            self.indexed_doc += f"{file_analysis}\n"
            return file_analysis
        except Exception as e:
            print(f"Error processing file {self.current_name}: {str(e)}")
            return None

    def _read_file(self) -> str:
        """Read file content."""
        file_path = os.path.join(self.current_path, self.current_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise IOError(f"Error reading file {self.current_name}: {str(e)}")

    def walk_through_project(self, path: str) -> None:
        """Walk through project directories and process files."""
        file_count = 0
        for root, dirs, files in os.walk(path):
            dirs[:] = [
                d for d in dirs if not self.should_ignore_dir(os.path.join(root, d))
            ]
            included_files = [
                f
                for f in files
                if any(
                    f.lower().endswith(ext.lower())
                    for ext in self.included_file_extensions
                )
            ]

            for file in included_files:
                self.current_path = root
                self.current_name = file
                self.process_file()
                file_count += 1
                if file_count % 3 == 0 or file_count % 4 == 0:
                    self.indexed_doc += f"\n{self.DOCUMENT_SEPARATOR}\n"

    def chunk_and_embed_documents(self) -> List[Dict]:
        """Chunk documents and create embeddings."""
        if not self.indexed_doc:
            return []

        documents = self.indexed_doc.split(self.DOCUMENT_SEPARATOR)
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

    def save_to_vector_db(self, embedded_chunks: List[Dict]) -> None:
        """Save embedded chunks to vector database."""
        texts = [chunk["text"] for chunk in embedded_chunks]
        vectors = [chunk["embedding"] for chunk in embedded_chunks]
        paths = [chunk["metadata"]["path"] for chunk in embedded_chunks]
        self.vector_db.insert(texts=texts, file_paths=paths, vectors=vectors)

    def save_collection_metadata(self) -> Dict:
        """Save collection metadata to database."""
        existing_collection = self.db_service.get_collection_by_path(self.base_path)
        if existing_collection:
            return existing_collection

        return self.db_service.create_project_collection(
            name=self.collection_name, path=self.base_path
        )

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

    def start_indexing(self, path: str) -> Dict:
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

            self.ignored_directories = configs.get("ignored-directories", [])
            self.included_file_extensions = configs.get("included-file-extensions", [])
            starting_directory = configs.get("starting-directory", "")

            self.base_path = path
            full_path = os.path.join(path, starting_directory)

            self.collection_name = self._generate_collection_name(full_path)
            self.vector_db = VectorDB(
                collection_name=self.collection_name, dim=self.DIMENSIONS
            )

            self.walk_through_project(full_path)
            embedded_chunks = self.chunk_and_embed_documents()
            self.save_to_vector_db(embedded_chunks)
            collection_info = self.save_collection_metadata()

            return {
                "success": True,
                "skip_indexing": False,
                "collection_name": self.collection_name,
                "collection_info": collection_info,
                "chunks_processed": len(embedded_chunks),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
