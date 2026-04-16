"""
File reader for repository ingestion.

This module handles reading source code files from cloned repositories,
applying filters to exclude binary files, dependencies, and build artifacts.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from app.utils.file_utils import (
    walk_directory,
    is_source_code_file,
    should_exclude_directory,
    should_exclude_file,
    is_binary_file,
    get_file_size,
    get_relative_path,
)
from app.utils.language_detector import (
    detect_language,
    detect_languages_in_directory,
    is_supported_language,
)


@dataclass
class FileInfo:
    """Information about a source code file."""
    
    absolute_path: str
    relative_path: str
    language: str
    size_bytes: int
    
    def __post_init__(self):
        """Validate file info after initialization."""
        if not os.path.exists(self.absolute_path):
            raise ValueError(f"File does not exist: {self.absolute_path}")


class FileReader:
    """
    Reads source code files from a repository directory.
    
    Filters out:
    - Binary files
    - Dependencies (node_modules, venv, etc.)
    - Build artifacts (dist, build, target, etc.)
    - Hidden files and directories (unless explicitly included)
    """
    
    def __init__(
        self,
        repository_path: str,
        include_hidden: bool = False,
        max_file_size_mb: float = 10.0,
        additional_excluded_dirs: Optional[Set[str]] = None,
    ):
        """
        Initialize the file reader.
        
        Args:
            repository_path: Path to the cloned repository
            include_hidden: Whether to include hidden files/directories
            max_file_size_mb: Maximum file size in MB to process
            additional_excluded_dirs: Additional directories to exclude
        """
        self.repository_path = os.path.abspath(repository_path)
        self.include_hidden = include_hidden
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
        self.additional_excluded_dirs = additional_excluded_dirs or set()
        
        if not os.path.isdir(self.repository_path):
            raise ValueError(f"Repository path is not a directory: {repository_path}")
    
    def read_files(self) -> List[FileInfo]:
        """
        Read all source code files from the repository.
        
        Returns:
            List of FileInfo objects for each source file
        """
        # Walk the directory tree
        source_files = walk_directory(
            self.repository_path,
            exclude_dirs=self.additional_excluded_dirs,
            include_hidden=self.include_hidden,
        )
        
        # Build FileInfo objects
        file_infos = []
        for file_path in source_files:
            try:
                # Check file size
                file_size = get_file_size(file_path)
                if file_size > self.max_file_size_bytes:
                    continue
                
                # Detect language
                language = detect_language(file_path)
                
                # Skip unsupported languages
                if not is_supported_language(language):
                    continue
                
                # Get relative path
                relative_path = get_relative_path(file_path, self.repository_path)
                
                # Create FileInfo
                file_info = FileInfo(
                    absolute_path=file_path,
                    relative_path=relative_path,
                    language=language,
                    size_bytes=file_size,
                )
                file_infos.append(file_info)
                
            except (IOError, OSError, ValueError) as e:
                # Skip files that can't be read
                continue
        
        return file_infos
    
    def get_language_statistics(self) -> Dict[str, int]:
        """
        Get statistics about languages in the repository.
        
        Returns:
            Dictionary mapping language names to file counts
        """
        return detect_languages_in_directory(self.repository_path)
    
    def read_file_content(self, file_path: str) -> str:
        """
        Read the content of a file.
        
        Args:
            file_path: Path to the file (absolute or relative to repository)
            
        Returns:
            File content as string
            
        Raises:
            ValueError: If file is binary or doesn't exist
            IOError: If file can't be read
        """
        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.repository_path, file_path)
        
        # Validate file
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        if is_binary_file(file_path):
            raise ValueError(f"File is binary: {file_path}")
        
        # Read content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")
    
    def filter_by_language(
        self,
        file_infos: List[FileInfo],
        languages: Set[str]
    ) -> List[FileInfo]:
        """
        Filter files by programming language.
        
        Args:
            file_infos: List of FileInfo objects
            languages: Set of language names to include
            
        Returns:
            Filtered list of FileInfo objects
        """
        return [
            file_info for file_info in file_infos
            if file_info.language in languages
        ]
    
    def filter_by_path_pattern(
        self,
        file_infos: List[FileInfo],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[FileInfo]:
        """
        Filter files by path patterns.
        
        Args:
            file_infos: List of FileInfo objects
            include_patterns: List of patterns to include (e.g., ['src/', 'lib/'])
            exclude_patterns: List of patterns to exclude (e.g., ['test/', 'tests/'])
            
        Returns:
            Filtered list of FileInfo objects
        """
        filtered = file_infos
        
        # Apply include patterns
        if include_patterns:
            filtered = [
                file_info for file_info in filtered
                if any(pattern in file_info.relative_path for pattern in include_patterns)
            ]
        
        # Apply exclude patterns
        if exclude_patterns:
            filtered = [
                file_info for file_info in filtered
                if not any(pattern in file_info.relative_path for pattern in exclude_patterns)
            ]
        
        return filtered
    
    def get_total_size(self, file_infos: List[FileInfo]) -> int:
        """
        Get the total size of all files in bytes.
        
        Args:
            file_infos: List of FileInfo objects
            
        Returns:
            Total size in bytes
        """
        return sum(file_info.size_bytes for file_info in file_infos)
    
    def get_file_count_by_language(
        self,
        file_infos: List[FileInfo]
    ) -> Dict[str, int]:
        """
        Get file count grouped by language.
        
        Args:
            file_infos: List of FileInfo objects
            
        Returns:
            Dictionary mapping language names to file counts
        """
        counts: Dict[str, int] = {}
        for file_info in file_infos:
            counts[file_info.language] = counts.get(file_info.language, 0) + 1
        return counts


def read_repository_files(
    repository_path: str,
    include_hidden: bool = False,
    max_file_size_mb: float = 10.0,
    languages: Optional[Set[str]] = None,
) -> List[FileInfo]:
    """
    Convenience function to read files from a repository.
    
    Args:
        repository_path: Path to the cloned repository
        include_hidden: Whether to include hidden files/directories
        max_file_size_mb: Maximum file size in MB to process
        languages: Optional set of languages to filter by
        
    Returns:
        List of FileInfo objects
    """
    reader = FileReader(
        repository_path=repository_path,
        include_hidden=include_hidden,
        max_file_size_mb=max_file_size_mb,
    )
    
    file_infos = reader.read_files()
    
    # Filter by language if specified
    if languages:
        file_infos = reader.filter_by_language(file_infos, languages)
    
    return file_infos
