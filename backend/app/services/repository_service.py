"""
Repository loader service for GitHub repository management.

This module provides functionality for cloning, validating, and managing GitHub repositories.
It handles URL validation, authentication, metadata extraction, and incremental updates.

Requirements:
- 1.1: Clone valid GitHub repository URLs to local storage
- 1.2: Extract repository metadata (name, owner, branch, commit hash)
- 1.3: Return descriptive errors for invalid or inaccessible repositories
- 1.4: Check for updates and pull latest changes for existing repositories
- 1.5: Support public and private repositories with authentication
- 1.6: Accept GitHub personal access tokens or SSH keys for authentication
"""

import asyncio
import logging
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RepositoryServiceError(Exception):
    """Base exception for repository service errors."""
    pass


class InvalidRepositoryURLError(RepositoryServiceError):
    """Raised when repository URL is invalid."""
    pass


class RepositoryAccessError(RepositoryServiceError):
    """Raised when repository cannot be accessed (authentication, network, etc.)."""
    pass


class RepositoryCloneError(RepositoryServiceError):
    """Raised when repository cloning fails."""
    pass


class RepositoryMetadataError(RepositoryServiceError):
    """Raised when repository metadata extraction fails."""
    pass


class RepositoryService:
    """
    Service for managing GitHub repository operations.
    
    This service handles:
    - URL validation and parsing
    - Repository cloning with authentication
    - Metadata extraction (owner, name, branch, commit hash)
    - Update detection and incremental pulls
    - Error handling with descriptive messages
    """
    
    # GitHub URL patterns
    HTTPS_PATTERN = re.compile(
        r'^https?://github\.com/(?P<owner>[^/]+)/(?P<name>[^/]+?)(\.git)?/?$',
        re.IGNORECASE
    )
    SSH_PATTERN = re.compile(
        r'^git@github\.com:(?P<owner>[^/]+)/(?P<name>[^/]+?)(\.git)?$',
        re.IGNORECASE
    )
    
    def __init__(self):
        """Initialize the repository service."""
        self.settings = get_settings()
        self.storage_path = self.settings.repo_storage_path
        
        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"RepositoryService initialized with storage path: {self.storage_path}")
    
    def validate_url(self, url: str) -> Tuple[str, str, str]:
        """
        Validate and parse a GitHub repository URL.
        
        Supports both HTTPS and SSH URL formats:
        - HTTPS: https://github.com/owner/repo or https://github.com/owner/repo.git
        - SSH: git@github.com:owner/repo or git@github.com:owner/repo.git
        
        Args:
            url: GitHub repository URL to validate
            
        Returns:
            Tuple of (normalized_url, owner, name)
            
        Raises:
            InvalidRepositoryURLError: If URL is invalid or not a GitHub URL
            
        Requirements:
            - 1.3: Return descriptive error for invalid URLs
        """
        if not url or not isinstance(url, str):
            raise InvalidRepositoryURLError("Repository URL must be a non-empty string")
        
        url = url.strip()
        
        # Try HTTPS pattern
        https_match = self.HTTPS_PATTERN.match(url)
        if https_match:
            owner = https_match.group('owner')
            name = https_match.group('name')
            # Normalize to HTTPS without .git suffix
            normalized_url = f"https://github.com/{owner}/{name}.git"
            return normalized_url, owner, name
        
        # Try SSH pattern
        ssh_match = self.SSH_PATTERN.match(url)
        if ssh_match:
            owner = ssh_match.group('owner')
            name = ssh_match.group('name')
            # Normalize to SSH format with .git suffix
            normalized_url = f"git@github.com:{owner}/{name}.git"
            return normalized_url, owner, name
        
        # URL doesn't match any pattern
        raise InvalidRepositoryURLError(
            f"Invalid GitHub repository URL: '{url}'. "
            "Expected format: 'https://github.com/owner/repo' or 'git@github.com:owner/repo'"
        )
    
    def get_repository_path(self, owner: str, name: str) -> Path:
        """
        Get the local storage path for a repository.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Path object for the repository directory
        """
        return self.storage_path / owner / name
    
    def repository_exists(self, owner: str, name: str) -> bool:
        """
        Check if a repository is already cloned locally.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            True if repository exists locally, False otherwise
        """
        repo_path = self.get_repository_path(owner, name)
        git_dir = repo_path / ".git"
        return repo_path.exists() and git_dir.exists() and git_dir.is_dir()
    
    async def clone_repository(
        self,
        url: str,
        auth_token: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Clone a GitHub repository to local storage.
        
        Supports authentication via:
        - Personal Access Token (PAT) for HTTPS URLs
        - SSH key for SSH URLs
        
        Args:
            url: GitHub repository URL
            auth_token: Optional GitHub personal access token for HTTPS authentication
            ssh_key_path: Optional path to SSH private key for SSH authentication
            
        Returns:
            Dictionary with repository metadata:
            - url: Normalized repository URL
            - owner: Repository owner
            - name: Repository name
            - path: Local storage path
            - branch: Default branch name
            - commit_hash: Latest commit SHA
            
        Raises:
            InvalidRepositoryURLError: If URL is invalid
            RepositoryAccessError: If repository cannot be accessed
            RepositoryCloneError: If cloning fails
            
        Requirements:
            - 1.1: Clone valid GitHub repository URLs
            - 1.5: Support public and private repositories with authentication
            - 1.6: Accept GitHub PAT or SSH keys
        """
        # Validate URL
        normalized_url, owner, name = self.validate_url(url)
        
        # Check if repository already exists
        if self.repository_exists(owner, name):
            logger.info(f"Repository {owner}/{name} already exists, checking for updates")
            return await self.update_repository(owner, name)
        
        # Prepare clone URL with authentication
        clone_url = self._prepare_clone_url(normalized_url, auth_token)
        
        # Get target path
        repo_path = self.get_repository_path(owner, name)
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare git command
        cmd = ["git", "clone", clone_url, str(repo_path)]
        
        # Prepare environment with SSH key if provided
        env = self._prepare_git_env(ssh_key_path)
        
        logger.info(f"Cloning repository {owner}/{name} from {url}")
        
        try:
            # Run git clone
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace').strip()
                
                # Parse error message for better user feedback
                if "Authentication failed" in error_msg or "Permission denied" in error_msg:
                    raise RepositoryAccessError(
                        f"Authentication failed for {url}. "
                        "Please check your credentials (PAT or SSH key)."
                    )
                elif "Repository not found" in error_msg or "not found" in error_msg.lower():
                    raise RepositoryAccessError(
                        f"Repository not found: {url}. "
                        "Please check the URL or verify you have access to this repository."
                    )
                elif "Could not resolve host" in error_msg:
                    raise RepositoryAccessError(
                        f"Network error: Could not connect to GitHub. "
                        "Please check your internet connection."
                    )
                else:
                    raise RepositoryCloneError(
                        f"Failed to clone repository {url}: {error_msg}"
                    )
            
            logger.info(f"Successfully cloned repository {owner}/{name}")
            
            # Extract metadata
            metadata = await self.extract_metadata(owner, name)
            
            return metadata
            
        except (RepositoryAccessError, RepositoryCloneError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error cloning repository {url}: {e}")
            raise RepositoryCloneError(
                f"Unexpected error cloning repository {url}: {str(e)}"
            )
    
    async def update_repository(self, owner: str, name: str) -> Dict[str, str]:
        """
        Update an existing repository by pulling latest changes.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Dictionary with updated repository metadata
            
        Raises:
            RepositoryServiceError: If repository doesn't exist or update fails
            
        Requirements:
            - 1.4: Check for updates and pull latest changes
        """
        if not self.repository_exists(owner, name):
            raise RepositoryServiceError(
                f"Repository {owner}/{name} does not exist locally"
            )
        
        repo_path = self.get_repository_path(owner, name)
        
        logger.info(f"Updating repository {owner}/{name}")
        
        try:
            # Get current commit hash before update
            old_commit = await self._get_commit_hash(repo_path)
            
            # Fetch latest changes
            await self._run_git_command(repo_path, ["fetch", "origin"])
            
            # Get default branch
            default_branch = await self._get_default_branch(repo_path)
            
            # Pull latest changes
            await self._run_git_command(
                repo_path,
                ["pull", "origin", default_branch]
            )
            
            # Get new commit hash
            new_commit = await self._get_commit_hash(repo_path)
            
            if old_commit != new_commit:
                logger.info(
                    f"Repository {owner}/{name} updated from {old_commit[:7]} to {new_commit[:7]}"
                )
            else:
                logger.info(f"Repository {owner}/{name} is already up to date")
            
            # Extract updated metadata
            metadata = await self.extract_metadata(owner, name)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to update repository {owner}/{name}: {e}")
            raise RepositoryServiceError(
                f"Failed to update repository {owner}/{name}: {str(e)}"
            )
    
    async def extract_metadata(self, owner: str, name: str) -> Dict[str, str]:
        """
        Extract metadata from a cloned repository.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Dictionary with repository metadata:
            - url: Repository URL
            - owner: Repository owner
            - name: Repository name
            - path: Local storage path
            - branch: Default branch name
            - commit_hash: Latest commit SHA
            
        Raises:
            RepositoryMetadataError: If metadata extraction fails
            
        Requirements:
            - 1.2: Extract repository metadata
        """
        if not self.repository_exists(owner, name):
            raise RepositoryMetadataError(
                f"Repository {owner}/{name} does not exist locally"
            )
        
        repo_path = self.get_repository_path(owner, name)
        
        try:
            # Get remote URL
            remote_url = await self._get_remote_url(repo_path)
            
            # Get default branch
            default_branch = await self._get_default_branch(repo_path)
            
            # Get latest commit hash
            commit_hash = await self._get_commit_hash(repo_path)
            
            metadata = {
                "url": remote_url,
                "owner": owner,
                "name": name,
                "path": str(repo_path),
                "branch": default_branch,
                "commit_hash": commit_hash,
            }
            
            logger.debug(f"Extracted metadata for {owner}/{name}: {metadata}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata for {owner}/{name}: {e}")
            raise RepositoryMetadataError(
                f"Failed to extract metadata for {owner}/{name}: {str(e)}"
            )
    
    async def has_updates(self, owner: str, name: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a repository has updates available.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Tuple of (has_updates, latest_remote_commit_hash)
            
        Raises:
            RepositoryServiceError: If check fails
            
        Requirements:
            - 1.4: Detect repository updates
        """
        if not self.repository_exists(owner, name):
            raise RepositoryServiceError(
                f"Repository {owner}/{name} does not exist locally"
            )
        
        repo_path = self.get_repository_path(owner, name)
        
        try:
            # Get current local commit
            local_commit = await self._get_commit_hash(repo_path)
            
            # Fetch latest changes without merging
            await self._run_git_command(repo_path, ["fetch", "origin"])
            
            # Get default branch
            default_branch = await self._get_default_branch(repo_path)
            
            # Get remote commit hash
            remote_commit = await self._run_git_command(
                repo_path,
                ["rev-parse", f"origin/{default_branch}"]
            )
            remote_commit = remote_commit.strip()
            
            has_updates = local_commit != remote_commit
            
            logger.debug(
                f"Repository {owner}/{name} update check: "
                f"local={local_commit[:7]}, remote={remote_commit[:7]}, "
                f"has_updates={has_updates}"
            )
            
            return has_updates, remote_commit
            
        except Exception as e:
            logger.error(f"Failed to check updates for {owner}/{name}: {e}")
            raise RepositoryServiceError(
                f"Failed to check updates for {owner}/{name}: {str(e)}"
            )
    
    # ============================================================================
    # Private Helper Methods
    # ============================================================================
    
    def _prepare_clone_url(self, url: str, auth_token: Optional[str] = None) -> str:
        """
        Prepare clone URL with authentication if provided.
        
        For HTTPS URLs with auth token, embeds token in URL.
        For SSH URLs, returns URL as-is (SSH key handled via environment).
        
        Args:
            url: Normalized repository URL
            auth_token: Optional GitHub personal access token
            
        Returns:
            Clone URL with authentication embedded if applicable
        """
        if url.startswith("https://") and auth_token:
            # Embed token in HTTPS URL
            # Format: https://token@github.com/owner/repo.git
            return url.replace("https://", f"https://{auth_token}@")
        else:
            return url
    
    def _prepare_git_env(self, ssh_key_path: Optional[str] = None) -> Optional[Dict[str, str]]:
        """
        Prepare environment variables for git command.
        
        If SSH key path is provided, sets GIT_SSH_COMMAND to use the key.
        
        Args:
            ssh_key_path: Optional path to SSH private key
            
        Returns:
            Environment dictionary or None
        """
        if ssh_key_path:
            import os
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = f"ssh -i {ssh_key_path} -o StrictHostKeyChecking=no"
            return env
        return None
    
    async def _run_git_command(
        self,
        repo_path: Path,
        args: list,
        env: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Run a git command in the repository directory.
        
        Args:
            repo_path: Path to repository
            args: Git command arguments (without 'git' prefix)
            env: Optional environment variables
            
        Returns:
            Command stdout output
            
        Raises:
            RepositoryServiceError: If command fails
        """
        cmd = ["git", "-C", str(repo_path)] + args
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='replace').strip()
                raise RepositoryServiceError(
                    f"Git command failed: {' '.join(args)}\nError: {error_msg}"
                )
            
            return stdout.decode('utf-8', errors='replace').strip()
            
        except RepositoryServiceError:
            raise
        except Exception as e:
            raise RepositoryServiceError(
                f"Failed to run git command {' '.join(args)}: {str(e)}"
            )
    
    async def _get_remote_url(self, repo_path: Path) -> str:
        """Get the remote origin URL."""
        return await self._run_git_command(
            repo_path,
            ["config", "--get", "remote.origin.url"]
        )
    
    async def _get_default_branch(self, repo_path: Path) -> str:
        """Get the default branch name."""
        try:
            # Try to get the default branch from remote
            branch = await self._run_git_command(
                repo_path,
                ["symbolic-ref", "refs/remotes/origin/HEAD"]
            )
            # Extract branch name from refs/remotes/origin/main
            return branch.split("/")[-1]
        except RepositoryServiceError:
            # Fallback: get current branch
            return await self._run_git_command(
                repo_path,
                ["rev-parse", "--abbrev-ref", "HEAD"]
            )
    
    async def _get_commit_hash(self, repo_path: Path) -> str:
        """Get the latest commit hash."""
        return await self._run_git_command(
            repo_path,
            ["rev-parse", "HEAD"]
        )
