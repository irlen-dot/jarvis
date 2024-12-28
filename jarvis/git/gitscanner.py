from git import Repo
from typing import Dict, List, Optional
from enum import Enum
import os


class ChangeType(Enum):
    MODIFIED = "M"
    ADDED = "A"
    DELETED = "D"
    RENAMED = "R"
    UNTRACKED = "?"


class GitChangeScanner:
    def __init__(self, repo_path: str = "."):
        """
        Initialize the GitChangeScanner.

        Args:
            repo_path (str): Path to the Git repository. Defaults to current directory.
        """
        self.repo_path = os.path.abspath(repo_path)
        try:
            self.repo = Repo(self.repo_path)
            if not self.repo.git_dir:
                raise ValueError("Not a git repository")
        except Exception as e:
            raise ValueError(f"Error initializing repository: {str(e)}")

    def get_changes(
        self, include_untracked: bool = True
    ) -> Dict[ChangeType, List[str]]:
        """
        Get all changes in the repository.

        Args:
            include_untracked (bool): Whether to include untracked files. Defaults to True.

        Returns:
            Dict[ChangeType, List[str]]: Dictionary of changes grouped by type
        """
        changes = {
            ChangeType.MODIFIED: [],
            ChangeType.ADDED: [],
            ChangeType.DELETED: [],
            ChangeType.RENAMED: [],
            ChangeType.UNTRACKED: [],
        }

        # Get changes between working directory and HEAD
        diff = self.repo.head.commit.diff(None)

        # Handle modified, added, deleted, and renamed files
        for item in diff:
            if item.change_type == "M":
                changes[ChangeType.MODIFIED].append(item.a_path)
            elif item.change_type == "A":
                changes[ChangeType.ADDED].append(item.a_path)
            elif item.change_type == "D":
                changes[ChangeType.DELETED].append(item.a_path)
            elif item.change_type == "R":
                changes[ChangeType.RENAMED].append(f"{item.a_path} -> {item.b_path}")

        # Handle untracked files if requested
        if include_untracked:
            untracked = self.repo.untracked_files
            changes[ChangeType.UNTRACKED].extend(untracked)

        return changes

    def get_staged_changes(self) -> Dict[ChangeType, List[str]]:
        """
        Get only staged changes in the repository.

        Returns:
            Dict[ChangeType, List[str]]: Dictionary of staged changes grouped by type
        """
        changes = {
            ChangeType.MODIFIED: [],
            ChangeType.ADDED: [],
            ChangeType.DELETED: [],
            ChangeType.RENAMED: [],
        }

        # Get changes between HEAD and index (staged changes)
        diff = self.repo.head.commit.diff()

        for item in diff:
            if item.change_type == "M":
                changes[ChangeType.MODIFIED].append(item.a_path)
            elif item.change_type == "A":
                changes[ChangeType.ADDED].append(item.a_path)
            elif item.change_type == "D":
                changes[ChangeType.DELETED].append(item.a_path)
            elif item.change_type == "R":
                changes[ChangeType.RENAMED].append(f"{item.a_path} -> {item.b_path}")

        return changes

    def print_changes(self, changes: Dict[ChangeType, List[str]]) -> None:
        """
        Print changes in a formatted way.

        Args:
            changes (Dict[ChangeType, List[str]]): Dictionary of changes to print
        """
        for change_type, files in changes.items():
            if files:
                print(f"\n{change_type.name}:")
                for file in files:
                    print(f"  - {file}")
