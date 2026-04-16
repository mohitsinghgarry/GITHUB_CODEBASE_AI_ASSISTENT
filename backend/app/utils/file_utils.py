"""
File utility functions for filtering and validation.

This module provides utilities for:
- Detecting binary files
- Filtering out dependencies and build artifacts
- Validating file paths
- Checking file types
"""

import os
import mimetypes
from pathlib import Path
from typing import Set, List


# Binary file extensions to exclude
BINARY_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp', '.tiff',
    # Videos
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm',
    # Audio
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma',
    # Archives
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.xz',
    # Executables and binaries
    '.exe', '.dll', '.so', '.dylib', '.bin', '.o', '.a', '.lib',
    # Documents (binary formats)
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    # Database files
    '.db', '.sqlite', '.sqlite3',
    # Other binary formats
    '.pyc', '.pyo', '.class', '.jar', '.war', '.ear',
}

# Directories to exclude (dependencies and build artifacts)
EXCLUDED_DIRECTORIES = {
    # Node.js
    'node_modules',
    # Python
    'venv', 'env', '.venv', '.env', '__pycache__', '.pytest_cache',
    '.mypy_cache', '.tox', '.eggs', '*.egg-info', 'dist', 'build',
    # Java/Kotlin
    'target', 'build', '.gradle',
    # Ruby
    'vendor', '.bundle',
    # Go
    'vendor',
    # Rust
    'target',
    # C/C++
    'build', 'cmake-build-debug', 'cmake-build-release',
    # IDE and editor directories
    '.idea', '.vscode', '.vs', '.eclipse', '.settings',
    # Version control
    '.git', '.svn', '.hg', '.bzr',
    # OS specific
    '.DS_Store', 'Thumbs.db',
    # Build artifacts
    'dist', 'out', 'bin', 'obj',
    # Documentation builds
    '_build', 'site', '.docusaurus',
    # Test coverage
    'coverage', '.coverage', 'htmlcov', '.nyc_output',
    # Temporary files
    'tmp', 'temp', '.tmp', '.temp',
    # Package managers
    '.npm', '.yarn', '.pnpm-store',
}

# File patterns to exclude
EXCLUDED_FILE_PATTERNS = {
    # Lock files
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Pipfile.lock',
    'poetry.lock', 'Gemfile.lock', 'Cargo.lock', 'composer.lock',
    # Minified files
    '*.min.js', '*.min.css',
    # Source maps
    '*.map',
    # Log files
    '*.log',
    # Environment files (may contain secrets)
    '.env', '.env.local', '.env.production', '.env.development',
    # IDE files
    '*.swp', '*.swo', '*~',
}


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary based on extension and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is binary, False otherwise
    """
    # Check extension first (fast)
    ext = Path(file_path).suffix.lower()
    if ext in BINARY_EXTENSIONS:
        return True
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        # Allow text/* types
        if mime_type.startswith('text/'):
            return False
        # Allow specific application/* types that are text-based
        text_based_mime_types = {
            'application/json',
            'application/xml',
            'application/javascript',
            'application/x-javascript',
            'application/typescript',
            'application/x-typescript',
            'application/x-yaml',
            'application/yaml',
        }
        if mime_type in text_based_mime_types:
            return False
        # Other application/* types might be binary, check content
    
    # Check file content (read first 8KB)
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8')
                return False
            except UnicodeDecodeError:
                return True
    except (IOError, OSError):
        # If we can't read the file, assume it's binary
        return True


def should_exclude_directory(dir_name: str) -> bool:
    """
    Check if a directory should be excluded from processing.
    
    Args:
        dir_name: Name of the directory
        
    Returns:
        True if the directory should be excluded, False otherwise
    """
    return dir_name in EXCLUDED_DIRECTORIES or dir_name.startswith('.')


def should_exclude_file(file_path: str) -> bool:
    """
    Check if a file should be excluded from processing.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file should be excluded, False otherwise
    """
    file_name = os.path.basename(file_path)
    
    # Check exact matches
    if file_name in EXCLUDED_FILE_PATTERNS:
        return True
    
    # Check patterns (simple wildcard matching)
    for pattern in EXCLUDED_FILE_PATTERNS:
        if '*' in pattern:
            # Simple wildcard matching
            if pattern.startswith('*'):
                suffix = pattern[1:]
                if file_name.endswith(suffix):
                    return True
            elif pattern.endswith('*'):
                prefix = pattern[:-1]
                if file_name.startswith(prefix):
                    return True
    
    return False


def is_source_code_file(file_path: str) -> bool:
    """
    Check if a file is a source code file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a source code file, False otherwise
    """
    # Check if it's not binary
    if is_binary_file(file_path):
        return False
    
    # Check if it should be excluded
    if should_exclude_file(file_path):
        return False
    
    # Check if it has a known source code extension
    ext = Path(file_path).suffix.lower()
    source_extensions = {
        # Programming languages
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.cc',
        '.h', '.hpp', '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt',
        '.scala', '.r', '.m', '.mm', '.dart', '.lua', '.pl', '.sh', '.bash',
        '.zsh', '.fish', '.ps1', '.psm1', '.mjs', '.cjs', '.mts', '.cts',
        # Web
        '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
        # Config and data
        '.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.cfg', '.conf',
        # Documentation
        '.md', '.rst', '.txt', '.adoc', '.markdown',
        # SQL
        '.sql',
        # Other
        '.proto', '.graphql', '.gql', '.dockerfile', '.makefile',
    }
    
    return ext in source_extensions


def filter_files(file_paths: List[str]) -> List[str]:
    """
    Filter a list of file paths to include only source code files.
    
    Args:
        file_paths: List of file paths to filter
        
    Returns:
        Filtered list of source code file paths
    """
    filtered = []
    for file_path in file_paths:
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            continue
        
        # Skip if it's a directory
        if os.path.isdir(file_path):
            continue
        
        # Skip if it should be excluded
        if should_exclude_file(file_path):
            continue
        
        # Skip if it's binary
        if is_binary_file(file_path):
            continue
        
        # Include if it's a source code file
        if is_source_code_file(file_path):
            filtered.append(file_path)
    
    return filtered


def walk_directory(
    root_path: str,
    exclude_dirs: Set[str] = None,
    include_hidden: bool = False
) -> List[str]:
    """
    Walk a directory tree and return all source code file paths.
    
    Args:
        root_path: Root directory to walk
        exclude_dirs: Additional directories to exclude
        include_hidden: Whether to include hidden files/directories
        
    Returns:
        List of source code file paths
    """
    if exclude_dirs is None:
        exclude_dirs = set()
    
    # Combine with default excluded directories
    all_excluded = EXCLUDED_DIRECTORIES | exclude_dirs
    
    source_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out excluded directories (modifies dirnames in-place)
        filtered_dirs = []
        for d in dirnames:
            # Skip if in excluded list
            if d in all_excluded:
                continue
            # Skip if it's a known excluded directory (but not hidden)
            if d in EXCLUDED_DIRECTORIES and not d.startswith('.'):
                continue
            # Skip hidden directories if not included
            if d.startswith('.') and not include_hidden:
                continue
            filtered_dirs.append(d)
        dirnames[:] = filtered_dirs
        
        # Process files in current directory
        for filename in filenames:
            # Skip hidden files if not included
            if not include_hidden and filename.startswith('.'):
                continue
            
            file_path = os.path.join(dirpath, filename)
            
            # Check if it's a source code file
            if is_source_code_file(file_path):
                source_files.append(file_path)
    
    return source_files


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (IOError, OSError):
        return 0


def get_relative_path(file_path: str, root_path: str) -> str:
    """
    Get the relative path of a file from a root directory.
    
    Args:
        file_path: Absolute path to the file
        root_path: Root directory path
        
    Returns:
        Relative path from root to file
    """
    return os.path.relpath(file_path, root_path)
