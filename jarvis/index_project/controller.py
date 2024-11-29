from jarvis.helper.cmd_dirs_to_json import parse_dir_output
from jarvis.helper.cmd_prompt import change_dir, run_command
from jarvis.index_project.agent import IndexCodeAgent
import os


class IndexController:
    EXCLUDED_EXTENSIONS = {".meta", ".cs.meta"}

    def __init__(self):
        self.index_code_agent = IndexCodeAgent()
        self.base_path = ""

    def start_indexing(self, path: str):
        self.base_path = path
        self._index_directory(path)

    def _index_directory(self, current_path: str):
        with change_dir(current_path):
            _, output = run_command("dir")
            folders_files = parse_dir_output(output)

            # Process files
            files = folders_files.get("files", [])
            for file in files:
                file_name = file.get("name")
                if file_name.endswith(".cs"):
                    self.current_name = file_name
                    self.process_file(current_path)

            # Process subdirectories
            folders = folders_files.get("directories", [])
            for folder_name in folders:

                # TODO filter everything on the parsing stage.
                if folder_name in [".", ".."]:
                    continue

                folder_path = os.path.join(current_path, folder_name)
                self._index_directory(folder_path)

    def process_file(self, current_path: str) -> None:
        content = self.open_file()
        file_analyzes = self.index_code_agent.start_indexing(content)
        rel_path = os.path.relpath(
            os.path.join(current_path, self.current_name), self.base_path
        )
        file_analyzes = file_analyzes + f"\npath: {rel_path}"
        print(file_analyzes)

        return file_analyzes

    def open_file(self) -> str:
        file_name = self.current_name
        with open(file_name, "r") as file:
            lines = file.readlines()
            return "\n".join(lines)
