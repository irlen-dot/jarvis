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

    def start_indexing(self, path: str):
        self.base_path = path
        self._index_directory(path)

    def _index_directory(self, current_path: str):
        with change_dir(current_path):
            self.indexed_doc = ""
            self.current_path = current_path
            _, output = run_command("dir")
            self.folders_files = parse_dir_output(output)

            # Process files
            self.index_folders()

            # Process subdirectories
            self.index_files()

    def index_files(self):
        files = self.folders_files.get("files", [])
        for file in files:
            file_name = file.get("name")
            if file_name.endswith(".cs"):
                self.current_name = file_name
                self.process_file(self.current_path)

            
            
    def index_folders(self):
            folders = self.folders_files.get("directories", [])
            for folder_name in folders:
                if folder_name in [".", ".."]:
                    continue
                folder_path = os.path.join(self.current_path, folder_name)
                self._index_directory(folder_path)

    def process_file(self, current_path: str) -> None:
        content = self.open_file()
        file_analyzes = self.index_code_agent.start_indexing(content)
        rel_path = os.path.relpath(
            os.path.join(current_path, self.current_name), self.base_path
        )
        file_analyzes = file_analyzes + f"\npath: {rel_path}"
        
        # Add the file analysis and separator to the indexed document
        self.indexed_doc += f"{file_analyzes}\n{self.DOCUMENT_SEPARATOR}\n"

        return file_analyzes
    
    # def chunk_doc():


    # def open_file(self) -> str:
    #     file_name = self.current_name
    #     with open(file_name, "r") as file:
    #         lines = file.readlines()
    #         return "\n".join(lines)