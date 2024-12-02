from jarvis.helper.cmd_dirs_to_json import parse_dir_output
from jarvis.helper.cmd_prompt import change_dir, run_command
from jarvis.helper.embedding import EmbeddingService
from jarvis.helper.vector_db import VectorDB
from jarvis.index_project.agent import IndexCodeAgent
import os

class IndexController:
    EXCLUDED_EXTENSIONS = {".meta", ".cs.meta"}
    DIMENSIONS = 1536
    DOCUMENT_SEPARATOR = "===============CUT"

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index_code_agent = IndexCodeAgent()
        self.vector_db = VectorDB(collection_name="project_files", dim=self.DIMENSIONS)
        self.base_path = ""
        self.indexed_doc = ""

    def start_indexing(self, path: str):
        self.base_path = path
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith('.cs') and not any(file.endswith(ext) for ext in self.EXCLUDED_EXTENSIONS):
                    self.current_path = root
                    self.current_name = file
                    self.process_file()
            if any(f.endswith('.cs') for f in files):
                self.indexed_doc += f"\n{self.DOCUMENT_SEPARATOR}\n"
        print(f"Final indexed document:\n{self.indexed_doc}")
        self.chunk_doc()

    def process_file(self) -> None:
        try:
            content = self.open_file()
            file_analyzes = self.index_code_agent.start_indexing(content)
            abs_path = os.path.abspath(os.path.join(self.current_path, self.current_name))
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
            path_line = [line for line in chunk.split('\n') if line.startswith('path: ')]
            if path_line:
                metadata['path'] = path_line[0].replace('path: ', '')
            embeddings_input.append({'text': chunk, 'metadata': metadata})

        # Get embeddings and store in vector DB
        embedded_chunks = self.embedding_service.embed_chunks(embeddings_input)

        texts = [chunk['text'] for chunk in embedded_chunks]
        vectors = [chunk['embedding'] for chunk in embedded_chunks]
        paths = [chunk['metadata']['path'] for chunk in embedded_chunks]

        # Store in vector DB
        self.vector_db.insert(texts=texts, file_paths=paths, vectors=vectors)

        return embedded_chunks

    def open_file(self) -> str:
        try:
            file_path = os.path.join(self.current_path, self.current_name)
            with open(file_path, "r", encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {self.current_name}: {str(e)}")
            raise