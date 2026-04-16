"""
Unit tests for RepositoryService.

Tests URL validation, authentication handling, and metadata extraction.

Requirements:
- 1.1: Test URL validation with valid and invalid formats
- 1.2: Test authentication error handling
- 1.3: Test metadata extraction
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.repository_service import (
    RepositoryService,
    InvalidRepositoryURLError,
    RepositoryAccessError,
    RepositoryCloneError,
    RepositoryMetadataError,
    RepositoryServiceError,
)


class TestRepositoryServiceURLValidation:
    """Test URL validation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    def test_validate_https_url_basic(self):
        """Test validation of basic HTTPS URL."""
        url = "https://github.com/owner/repo"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_https_url_with_git_suffix(self):
        """Test validation of HTTPS URL with .git suffix."""
        url = "https://github.com/owner/repo.git"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_https_url_with_trailing_slash(self):
        """Test validation of HTTPS URL with trailing slash."""
        url = "https://github.com/owner/repo/"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_http_url(self):
        """Test validation of HTTP URL (should work)."""
        url = "http://github.com/owner/repo"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_ssh_url_basic(self):
        """Test validation of basic SSH URL."""
        url = "git@github.com:owner/repo"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "git@github.com:owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_ssh_url_with_git_suffix(self):
        """Test validation of SSH URL with .git suffix."""
        url = "git@github.com:owner/repo.git"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "git@github.com:owner/repo.git"
        assert owner == "owner"
        assert name == "repo"
    
    def test_validate_url_with_hyphens_and_underscores(self):
        """Test validation with hyphens and underscores in names."""
        url = "https://github.com/my-org/my_repo-name"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/my-org/my_repo-name.git"
        assert owner == "my-org"
        assert name == "my_repo-name"
    
    def test_validate_url_case_insensitive(self):
        """Test that URL validation is case-insensitive."""
        url = "HTTPS://GITHUB.COM/Owner/Repo"
        normalized, owner, name = self.service.validate_url(url)
        
        assert normalized == "https://github.com/Owner/Repo.git"
        assert owner == "Owner"
        assert name == "Repo"
    
    def test_validate_empty_url(self):
        """Test validation of empty URL."""
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url("")
        
        assert "non-empty string" in str(exc_info.value)
    
    def test_validate_none_url(self):
        """Test validation of None URL."""
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url(None)
        
        assert "non-empty string" in str(exc_info.value)
    
    def test_validate_non_github_url(self):
        """Test validation of non-GitHub URL."""
        url = "https://gitlab.com/owner/repo"
        
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url(url)
        
        assert "Invalid GitHub repository URL" in str(exc_info.value)
        assert "Expected format" in str(exc_info.value)
    
    def test_validate_malformed_url(self):
        """Test validation of malformed URL."""
        url = "not-a-url"
        
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url(url)
        
        assert "Invalid GitHub repository URL" in str(exc_info.value)
    
    def test_validate_url_missing_owner(self):
        """Test validation of URL missing owner."""
        url = "https://github.com/repo"
        
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url(url)
        
        assert "Invalid GitHub repository URL" in str(exc_info.value)
    
    def test_validate_url_missing_repo(self):
        """Test validation of URL missing repository name."""
        url = "https://github.com/owner/"
        
        with pytest.raises(InvalidRepositoryURLError) as exc_info:
            self.service.validate_url(url)
        
        assert "Invalid GitHub repository URL" in str(exc_info.value)


class TestRepositoryServicePaths:
    """Test repository path management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    def test_get_repository_path(self):
        """Test getting repository path."""
        path = self.service.get_repository_path("owner", "repo")
        
        assert isinstance(path, Path)
        assert path.name == "repo"
        assert path.parent.name == "owner"
    
    def test_repository_exists_false(self, tmp_path):
        """Test repository_exists returns False for non-existent repo."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        exists = self.service.repository_exists("owner", "repo")
        
        assert exists is False
    
    def test_repository_exists_true(self, tmp_path):
        """Test repository_exists returns True for existing repo."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository structure
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        exists = self.service.repository_exists("owner", "repo")
        
        assert exists is True
    
    def test_repository_exists_false_without_git_dir(self, tmp_path):
        """Test repository_exists returns False if .git directory missing."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository directory but no .git
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        
        exists = self.service.repository_exists("owner", "repo")
        
        assert exists is False


class TestRepositoryServiceClone:
    """Test repository cloning functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    @pytest.mark.asyncio
    async def test_clone_repository_invalid_url(self):
        """Test cloning with invalid URL raises error."""
        with pytest.raises(InvalidRepositoryURLError):
            await self.service.clone_repository("not-a-url")
    
    @pytest.mark.asyncio
    async def test_clone_repository_success(self, tmp_path):
        """Test successful repository cloning."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/repo"
        
        # Mock subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            # Mock successful clone
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process
            
            # Mock metadata extraction
            with patch.object(self.service, 'extract_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    "url": url,
                    "owner": "owner",
                    "name": "repo",
                    "path": str(tmp_path / "owner" / "repo"),
                    "branch": "main",
                    "commit_hash": "abc123",
                }
                
                result = await self.service.clone_repository(url)
                
                assert result["owner"] == "owner"
                assert result["name"] == "repo"
                assert result["branch"] == "main"
                assert result["commit_hash"] == "abc123"
                
                # Verify git clone was called
                mock_exec.assert_called_once()
                call_args = mock_exec.call_args[0]
                assert call_args[0] == "git"
                assert call_args[1] == "clone"
    
    @pytest.mark.asyncio
    async def test_clone_repository_with_auth_token(self, tmp_path):
        """Test cloning with authentication token."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/repo"
        auth_token = "ghp_test_token_123"
        
        # Mock subprocess execution
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate = AsyncMock(return_value=(b"", b""))
            mock_exec.return_value = mock_process
            
            # Mock metadata extraction
            with patch.object(self.service, 'extract_metadata') as mock_metadata:
                mock_metadata.return_value = {
                    "url": url,
                    "owner": "owner",
                    "name": "repo",
                    "path": str(tmp_path / "owner" / "repo"),
                    "branch": "main",
                    "commit_hash": "abc123",
                }
                
                await self.service.clone_repository(url, auth_token=auth_token)
                
                # Verify token was embedded in URL
                call_args = mock_exec.call_args[0]
                clone_url = call_args[2]
                assert auth_token in clone_url
                assert clone_url.startswith(f"https://{auth_token}@")
    
    @pytest.mark.asyncio
    async def test_clone_repository_authentication_failed(self, tmp_path):
        """Test cloning with authentication failure."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/private-repo"
        
        # Mock subprocess execution with auth error
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 128
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"Authentication failed for 'https://github.com/owner/private-repo'")
            )
            mock_exec.return_value = mock_process
            
            with pytest.raises(RepositoryAccessError) as exc_info:
                await self.service.clone_repository(url)
            
            assert "Authentication failed" in str(exc_info.value)
            assert "credentials" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_clone_repository_not_found(self, tmp_path):
        """Test cloning non-existent repository."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/nonexistent"
        
        # Mock subprocess execution with not found error
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 128
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"Repository not found")
            )
            mock_exec.return_value = mock_process
            
            with pytest.raises(RepositoryAccessError) as exc_info:
                await self.service.clone_repository(url)
            
            assert "not found" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_clone_repository_network_error(self, tmp_path):
        """Test cloning with network error."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/repo"
        
        # Mock subprocess execution with network error
        with patch('asyncio.create_subprocess_exec') as mock_exec:
            mock_process = AsyncMock()
            mock_process.returncode = 128
            mock_process.communicate = AsyncMock(
                return_value=(b"", b"Could not resolve host: github.com")
            )
            mock_exec.return_value = mock_process
            
            with pytest.raises(RepositoryAccessError) as exc_info:
                await self.service.clone_repository(url)
            
            assert "Network error" in str(exc_info.value)
            assert "internet connection" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_clone_repository_already_exists(self, tmp_path):
        """Test cloning when repository already exists calls update."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        url = "https://github.com/owner/repo"
        
        # Create existing repository
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Mock update_repository
        with patch.object(self.service, 'update_repository') as mock_update:
            mock_update.return_value = {
                "url": url,
                "owner": "owner",
                "name": "repo",
                "path": str(repo_path),
                "branch": "main",
                "commit_hash": "abc123",
            }
            
            result = await self.service.clone_repository(url)
            
            # Verify update was called instead of clone
            mock_update.assert_called_once_with("owner", "repo")
            assert result["owner"] == "owner"


class TestRepositoryServiceMetadata:
    """Test metadata extraction functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    @pytest.mark.asyncio
    async def test_extract_metadata_success(self, tmp_path):
        """Test successful metadata extraction."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository structure
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Mock git commands
        with patch.object(self.service, '_get_remote_url') as mock_url, \
             patch.object(self.service, '_get_default_branch') as mock_branch, \
             patch.object(self.service, '_get_commit_hash') as mock_hash:
            
            mock_url.return_value = "https://github.com/owner/repo.git"
            mock_branch.return_value = "main"
            mock_hash.return_value = "abc123def456"
            
            metadata = await self.service.extract_metadata("owner", "repo")
            
            assert metadata["url"] == "https://github.com/owner/repo.git"
            assert metadata["owner"] == "owner"
            assert metadata["name"] == "repo"
            assert metadata["branch"] == "main"
            assert metadata["commit_hash"] == "abc123def456"
            assert "path" in metadata
    
    @pytest.mark.asyncio
    async def test_extract_metadata_repository_not_exists(self, tmp_path):
        """Test metadata extraction for non-existent repository."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        with pytest.raises(RepositoryMetadataError) as exc_info:
            await self.service.extract_metadata("owner", "repo")
        
        assert "does not exist locally" in str(exc_info.value)


class TestRepositoryServiceUpdate:
    """Test repository update functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    @pytest.mark.asyncio
    async def test_update_repository_success(self, tmp_path):
        """Test successful repository update."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository structure
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Mock git commands
        with patch.object(self.service, '_get_commit_hash') as mock_hash, \
             patch.object(self.service, '_run_git_command') as mock_git, \
             patch.object(self.service, '_get_default_branch') as mock_branch, \
             patch.object(self.service, 'extract_metadata') as mock_metadata:
            
            # Simulate commit change
            mock_hash.side_effect = ["old_commit", "new_commit"]
            mock_branch.return_value = "main"
            mock_git.return_value = ""
            mock_metadata.return_value = {
                "url": "https://github.com/owner/repo.git",
                "owner": "owner",
                "name": "repo",
                "path": str(repo_path),
                "branch": "main",
                "commit_hash": "new_commit",
            }
            
            result = await self.service.update_repository("owner", "repo")
            
            assert result["commit_hash"] == "new_commit"
            
            # Verify git commands were called
            assert mock_git.call_count >= 2  # fetch and pull
    
    @pytest.mark.asyncio
    async def test_update_repository_not_exists(self, tmp_path):
        """Test updating non-existent repository."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        with pytest.raises(RepositoryServiceError) as exc_info:
            await self.service.update_repository("owner", "repo")
        
        assert "does not exist locally" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_has_updates_true(self, tmp_path):
        """Test checking for updates when updates are available."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository structure
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Mock git commands
        with patch.object(self.service, '_get_commit_hash') as mock_hash, \
             patch.object(self.service, '_run_git_command') as mock_git, \
             patch.object(self.service, '_get_default_branch') as mock_branch:
            
            mock_hash.return_value = "local_commit"
            mock_branch.return_value = "main"
            mock_git.return_value = "remote_commit"
            
            has_updates, remote_commit = await self.service.has_updates("owner", "repo")
            
            assert has_updates is True
            assert remote_commit == "remote_commit"
    
    @pytest.mark.asyncio
    async def test_has_updates_false(self, tmp_path):
        """Test checking for updates when no updates available."""
        # Override storage path for testing
        self.service.storage_path = tmp_path
        
        # Create repository structure
        repo_path = tmp_path / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Mock git commands
        with patch.object(self.service, '_get_commit_hash') as mock_hash, \
             patch.object(self.service, '_run_git_command') as mock_git, \
             patch.object(self.service, '_get_default_branch') as mock_branch:
            
            mock_hash.return_value = "same_commit"
            mock_branch.return_value = "main"
            mock_git.return_value = "same_commit"
            
            has_updates, remote_commit = await self.service.has_updates("owner", "repo")
            
            assert has_updates is False
            assert remote_commit == "same_commit"


class TestRepositoryServiceHelpers:
    """Test helper methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = RepositoryService()
    
    def test_prepare_clone_url_https_with_token(self):
        """Test preparing HTTPS URL with auth token."""
        url = "https://github.com/owner/repo.git"
        token = "ghp_test_token"
        
        result = self.service._prepare_clone_url(url, token)
        
        assert result == f"https://{token}@github.com/owner/repo.git"
    
    def test_prepare_clone_url_https_without_token(self):
        """Test preparing HTTPS URL without auth token."""
        url = "https://github.com/owner/repo.git"
        
        result = self.service._prepare_clone_url(url, None)
        
        assert result == url
    
    def test_prepare_clone_url_ssh(self):
        """Test preparing SSH URL (token ignored)."""
        url = "git@github.com:owner/repo.git"
        token = "ghp_test_token"
        
        result = self.service._prepare_clone_url(url, token)
        
        assert result == url
        assert token not in result
    
    def test_prepare_git_env_with_ssh_key(self):
        """Test preparing environment with SSH key."""
        ssh_key_path = "/path/to/key"
        
        env = self.service._prepare_git_env(ssh_key_path)
        
        assert env is not None
        assert "GIT_SSH_COMMAND" in env
        assert ssh_key_path in env["GIT_SSH_COMMAND"]
        assert "StrictHostKeyChecking=no" in env["GIT_SSH_COMMAND"]
    
    def test_prepare_git_env_without_ssh_key(self):
        """Test preparing environment without SSH key."""
        env = self.service._prepare_git_env(None)
        
        assert env is None
