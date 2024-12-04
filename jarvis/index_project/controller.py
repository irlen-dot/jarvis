import pdb
from jarvis.helper.cmd_dirs_to_json import parse_dir_output
from jarvis.helper.cmd_prompt import change_dir, run_command
from jarvis.helper.db import Database
from jarvis.helper.embedding import EmbeddingService
from jarvis.helper.vector_db import VectorDB
from jarvis.index_project.agent import IndexCodeAgent
import os


class IndexController:

    INCLUDED_EXTENSIONS = {".cs"}  # Only process .cs files, can be expanded as needed

    IGNORED_DIRECTORIES = {
        "StarterAssets",
    }

    DIMENSIONS = 1536
    DOCUMENT_SEPARATOR = "===============CUT==============="

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index_code_agent = IndexCodeAgent()
        self.db_service = Database()
        self.base_path = ""
        self.indexed_doc = ""

    def should_ignore_dir(self, dir_path: str) -> bool:
        dir_name = os.path.basename(dir_path)
        # Case-insensitive directory check
        return any(
            ignored.lower() == dir_name.lower() or ignored.lower() in dir_path.lower()
            for ignored in self.IGNORED_DIRECTORIES
        )

    def start_indexing(self, path: str, project_type: str):
        print(project_type)
        pdb.set_trace()
        self.base_path = path
        self.collection_name = os.path.basename(os.path.normpath(path)).replace(
            " ", "_"
        )
        self.vector_db = VectorDB(
            collection_name=self.collection_name, dim=self.DIMENSIONS
        )

        file_count = 0
        for root, dirs, files in os.walk(path):
            # Filter directories using case-insensitive patterns
            dirs[:] = [
                d for d in dirs if not self.should_ignore_dir(os.path.join(root, d))
            ]

            # Filter files based on included extensions
            included_files = [
                f
                for f in files
                if any(
                    f.lower().endswith(ext.lower()) for ext in self.INCLUDED_EXTENSIONS
                )
            ]

            for file in included_files:
                self.current_path = root
                self.current_name = file
                self.process_file()
                file_count += 1
                if file_count % 3 == 0 or file_count % 4 == 0:
                    self.indexed_doc += f"\n{self.DOCUMENT_SEPARATOR}\n"

        self.chunk_doc()
        self.save_collection()

    def save_collection(self):
        """Create a collection if it doesn't exist, otherwise return existing one"""
        existing_collection = self.db_service.get_collection_by_path(self.base_path)
        if existing_collection:
            return existing_collection

        return self.db_service.create_project_collection(
            name=self.collection_name, path=self.base_path
        )

    def process_file(self) -> None:
        try:
            content = self.open_file()
            file_analyzes = self.index_code_agent.start_indexing(content)
            abs_path = os.path.abspath(
                os.path.join(self.current_path, self.current_name)
            )
            file_analyzes = file_analyzes + f"\npath: {abs_path}"
            self.indexed_doc += f"{file_analyzes}\n"
            print(file_analyzes)
            return file_analyzes
        except Exception as e:
            print(f"Error processing file {self.current_name}: {str(e)}")

    def chunk_doc(self):
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

        # Get embeddings and store in vector DB
        embedded_chunks = self.embedding_service.embed_chunks(embeddings_input)

        texts = [chunk["text"] for chunk in embedded_chunks]
        vectors = [chunk["embedding"] for chunk in embedded_chunks]
        paths = [chunk["metadata"]["path"] for chunk in embedded_chunks]

        # Store in vector DB
        self.vector_db.insert(texts=texts, file_paths=paths, vectors=vectors)

        return embedded_chunks

    def open_file(self) -> str:
        try:
            file_path = os.path.join(self.current_path, self.current_name)
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {self.current_name}: {str(e)}")
            raise
