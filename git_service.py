"""Git service for file status indicators."""
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional


class GitStatus(Enum):
    """Git file status indicators."""
    CLEAN = "clean"
    MODIFIED = "modified"
    STAGED = "staged"
    DELETED = "deleted"
    UNTRACKED = "untracked"


class GitService:
    """Service for Git operations and status checking."""

    def __init__(self, path: Path) -> None:
        """Initialize Git service for a given path.

        Args:
            path: Path to the directory to check Git status for.
        """
        self.path = Path(path)

    def is_git_repository(self) -> bool:
        """Check if the current directory is a Git repository.

        Returns:
            True if in a Git repository, False otherwise.
        """
        return (self.path / ".git").exists()

    def get_file_status(self, file_path: str) -> Optional[GitStatus]:
        """Get Git status for a specific file.

        Args:
            file_path: Relative path to the file from repository root.

        Returns:
            GitStatus if in Git repo, None otherwise.
        """
        if not self.is_git_repository():
            return None

        try:
            # Get status for all files and find our file
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode != 0:
                return None

            output = result.stdout.strip()
            if not output:
                return GitStatus.CLEAN

            # Look for our file in the output
            for line in output.split('\n'):
                if line.endswith(file_path) or file_path in line:
                    status_code = line[:2]
                    
                    if status_code == " M":
                        return GitStatus.MODIFIED
                    elif status_code == "A ":
                        return GitStatus.STAGED
                    elif status_code == "D ":
                        return GitStatus.DELETED
                    elif status_code == "??":
                        return GitStatus.UNTRACKED

            # File not found in status output, assume clean
            return GitStatus.CLEAN

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def get_status_symbol(self, status: Optional[GitStatus]) -> str:
        """Get display symbol for Git status.

        Args:
            status: Git status to get symbol for.

        Returns:
            Symbol character for display.
        """
        symbols = {
            GitStatus.MODIFIED: "M",
            GitStatus.STAGED: "A",
            GitStatus.DELETED: "D",
            GitStatus.UNTRACKED: "?",
            GitStatus.CLEAN: "",
        }
        return symbols.get(status, "")

    def get_status_color(self, status: Optional[GitStatus]) -> str:
        """Get color name for Git status.

        Args:
            status: Git status to get color for.

        Returns:
            Color name for Textual styling.
        """
        colors = {
            GitStatus.MODIFIED: "yellow",
            GitStatus.STAGED: "green",
            GitStatus.DELETED: "red",
            GitStatus.UNTRACKED: "cyan",
            GitStatus.CLEAN: "",
        }
        return colors.get(status, "")
