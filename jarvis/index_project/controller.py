from jarvis.helper.cmd_dirs_to_json import parse_dir_output
from jarvis.helper.cmd_prompt import change_dir, run_command
from jarvis.helper.vector_db import VectorDB
from jarvis.index_project.agent import IndexCodeAgent
import os

class IndexController:
    EXCLUDED_EXTENSIONS = {".meta", ".cs.meta"}
    DIMENSIONS = 1536
    DOCUMENT_SEPARATOR = "===============CUT"

    def __init__(self):
        self.index_code_agent = IndexCodeAgent()
        self.vector_db = VectorDB(collection_name="project_files", dim=self.DIMENSIONS)
        self.base_path = ""
        self.indexed_doc = ""

    def start_indexing(self, path: str):
        self.base_path = path
        self._index_directory(path)
        self.chunk_doc()  # Process all documents at the end
        print(f"Indexed Doc: {self.indexed_doc}")

    def _index_directory(self, current_path: str):
        self.current_path = current_path
        with change_dir(current_path):
            _, output = run_command("dir")
            self.folders_files = parse_dir_output(output)
            self.index_files()
            self.index_folders()

    def index_files(self):
        files = self.folders_files.get("files", [])
        for file in files:
            file_name = file.get("name")
            if file_name.endswith(".cs") and not any(file_name.endswith(ext) for ext in self.EXCLUDED_EXTENSIONS):
                self.current_name = file_name
                self.process_file()

    def index_folders(self):
        folders = self.folders_files.get("directories", [])
        # Only process if it's actually a directory list (not a directory entry name)
        if isinstance(folders, list):
            for folder in folders:
                folder_name = folder.get("name") if isinstance(folder, dict) else folder
                if folder_name in [".", ".."]:
                    continue
                folder_path = os.path.join(self.current_path, folder_name)
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    self._index_directory(folder_path)

    def process_file(self) -> None:
       try:
           content = self.open_file()
           file_analyzes = self.index_code_agent.start_indexing(content)
           abs_path = os.path.abspath(os.path.join(self.current_path, self.current_name))
           file_analyzes = file_analyzes + f"\npath: {abs_path}"
           self.indexed_doc += f"{file_analyzes}\n{self.DOCUMENT_SEPARATOR}\n"
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

        print(f"The embedding input: {embeddings_input}")
        return embeddings_input

    def open_file(self) -> str:
        try:
            with open(self.current_name, "r", encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {self.current_name}: {str(e)}")
            raise