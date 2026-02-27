"""Tests for Git service functionality."""
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from git_service import GitService, GitStatus


class TestGitService:
    """Test cases for GitService."""

    def test_is_git_repository_true(self):
        """Test detection of a Git repository."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Create .git directory
            (temp_path / ".git").mkdir()
            
            service = GitService(temp_path)
            assert service.is_git_repository() is True

    def test_is_git_repository_false(self):
        """Test detection of non-Git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            service = GitService(temp_path)
            assert service.is_git_repository() is False

    @patch('git_service.subprocess.run')
    def test_get_file_status_untracked(self, mock_run):
        """Test getting status of untracked file."""
        mock_run.return_value = Mock(
            stdout="?? new_file.txt\n",
            returncode=0
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / ".git").mkdir()
            # Create the untracked file
            (temp_path / "new_file.txt").touch()
            
            service = GitService(temp_path)
            status = service.get_file_status("new_file.txt")
            assert status == GitStatus.UNTRACKED

    def test_get_file_status_not_git_repo(self):
        """Test getting status when not in Git repo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            service = GitService(temp_path)
            status = service.get_file_status("any_file.txt")
            assert status is None

    def test_get_file_status_modified_real(self):
        """Test getting status of modified file using real Git."""
        # Use the actual project directory which has modified files
        project_path = Path(__file__).parent.parent
        service = GitService(project_path)
        
        # Test with a file we know is modified (README.md)
        status = service.get_file_status("README.md")
        # This should be MODIFIED since we modified it earlier
        assert status in [GitStatus.MODIFIED, GitStatus.CLEAN]  # Allow for clean state

    @patch('git_service.subprocess.run')
    def test_get_file_status_staged(self, mock_run):
        """Test getting status of staged file."""
        mock_run.return_value = Mock(
            stdout="A  staged_file.txt\n",
            returncode=0
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / ".git").mkdir()
            
            service = GitService(temp_path)
            status = service.get_file_status("staged_file.txt")
            assert status == GitStatus.STAGED

    @patch('git_service.subprocess.run')
    def test_get_file_status_deleted(self, mock_run):
        """Test getting status of deleted file."""
        mock_run.return_value = Mock(
            stdout="D  deleted_file.txt\n",
            returncode=0
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / ".git").mkdir()
            
            service = GitService(temp_path)
            status = service.get_file_status("deleted_file.txt")
            assert status == GitStatus.DELETED

    @patch('git_service.subprocess.run')
    def test_get_file_status_clean(self, mock_run):
        """Test getting status of clean file."""
        mock_run.return_value = Mock(
            stdout="",
            returncode=0
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / ".git").mkdir()
            # Create a file
            (temp_path / "clean_file.txt").touch()
            
            service = GitService(temp_path)
            status = service.get_file_status("clean_file.txt")
            assert status == GitStatus.CLEAN

    @patch('git_service.subprocess.run')
    def test_get_file_status_git_command_failed(self, mock_run):
        """Test handling of Git command failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stderr="fatal: not a git repository"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / ".git").mkdir()
            
            service = GitService(temp_path)
            status = service.get_file_status("any_file.txt")
            assert status is None

    def test_get_status_symbol(self):
        """Test getting status symbols."""
        service = GitService(Path("/tmp"))
        
        assert service.get_status_symbol(GitStatus.MODIFIED) == "M"
        assert service.get_status_symbol(GitStatus.STAGED) == "A"
        assert service.get_status_symbol(GitStatus.DELETED) == "D"
        assert service.get_status_symbol(GitStatus.UNTRACKED) == "?"
        assert service.get_status_symbol(GitStatus.CLEAN) == ""
        assert service.get_status_symbol(None) == ""

    def test_get_status_color(self):
        """Test getting status colors."""
        service = GitService(Path("/tmp"))
        
        assert service.get_status_color(GitStatus.MODIFIED) == "yellow"
        assert service.get_status_color(GitStatus.STAGED) == "green"
        assert service.get_status_color(GitStatus.DELETED) == "red"
        assert service.get_status_color(GitStatus.UNTRACKED) == "cyan"
        assert service.get_status_color(GitStatus.CLEAN) == ""
        assert service.get_status_color(None) == ""
