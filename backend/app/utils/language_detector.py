"""
Programming language detection utilities.

This module provides utilities for detecting the programming language
of source code files based on file extensions and content analysis.
"""

import os
from pathlib import Path
from typing import Optional, Dict, List


# Language mappings by file extension
EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    # Python
    '.py': 'python',
    '.pyw': 'python',
    '.pyx': 'python',
    '.pxd': 'python',
    '.pyi': 'python',
    
    # JavaScript/TypeScript
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.mts': 'typescript',
    '.cts': 'typescript',
    
    # Java
    '.java': 'java',
    
    # C/C++
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.hpp': 'cpp',
    '.hh': 'cpp',
    '.hxx': 'cpp',
    '.C': 'cpp',
    '.H': 'cpp',
    
    # C#
    '.cs': 'csharp',
    '.csx': 'csharp',
    
    # Go
    '.go': 'go',
    
    # Rust
    '.rs': 'rust',
    
    # Ruby
    '.rb': 'ruby',
    '.rake': 'ruby',
    '.gemspec': 'ruby',
    
    # PHP
    '.php': 'php',
    '.php3': 'php',
    '.php4': 'php',
    '.php5': 'php',
    '.phtml': 'php',
    
    # Swift
    '.swift': 'swift',
    
    # Kotlin
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    
    # Scala
    '.scala': 'scala',
    '.sc': 'scala',
    
    # R
    '.r': 'r',
    '.R': 'r',
    
    # Objective-C
    '.m': 'objective-c',
    '.mm': 'objective-c',
    
    # Dart
    '.dart': 'dart',
    
    # Lua
    '.lua': 'lua',
    
    # Perl
    '.pl': 'perl',
    '.pm': 'perl',
    '.t': 'perl',
    
    # Shell
    '.sh': 'shell',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    
    # PowerShell
    '.ps1': 'powershell',
    '.psm1': 'powershell',
    '.psd1': 'powershell',
    
    # Web
    '.html': 'html',
    '.htm': 'html',
    '.xhtml': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.vue': 'vue',
    '.svelte': 'svelte',
    
    # Config and data
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.xml': 'xml',
    '.ini': 'ini',
    '.cfg': 'ini',
    '.conf': 'conf',
    
    # Documentation
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.rst': 'restructuredtext',
    '.txt': 'text',
    '.adoc': 'asciidoc',
    
    # SQL
    '.sql': 'sql',
    
    # Other
    '.proto': 'protobuf',
    '.graphql': 'graphql',
    '.gql': 'graphql',
    '.dockerfile': 'dockerfile',
    '.makefile': 'makefile',
    '.cmake': 'cmake',
    '.gradle': 'gradle',
}

# Special filenames that indicate a specific language
FILENAME_TO_LANGUAGE: Dict[str, str] = {
    'Dockerfile': 'dockerfile',
    'Makefile': 'makefile',
    'Rakefile': 'ruby',
    'Gemfile': 'ruby',
    'Vagrantfile': 'ruby',
    'CMakeLists.txt': 'cmake',
    'build.gradle': 'gradle',
    'build.gradle.kts': 'kotlin',
    'settings.gradle': 'gradle',
    'settings.gradle.kts': 'kotlin',
    'pom.xml': 'xml',
    'package.json': 'json',
    'tsconfig.json': 'json',
    'composer.json': 'json',
    'Cargo.toml': 'toml',
    'pyproject.toml': 'toml',
    '.gitignore': 'text',
    '.dockerignore': 'text',
    'README': 'text',
    'LICENSE': 'text',
    'CHANGELOG': 'text',
}

# Shebang patterns for script detection
SHEBANG_TO_LANGUAGE: Dict[str, str] = {
    'python': 'python',
    'python2': 'python',
    'python3': 'python',
    'node': 'javascript',
    'bash': 'bash',
    'sh': 'shell',
    'zsh': 'zsh',
    'fish': 'fish',
    'ruby': 'ruby',
    'perl': 'perl',
    'php': 'php',
    'lua': 'lua',
}


def detect_language_from_extension(file_path: str) -> Optional[str]:
    """
    Detect programming language from file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or None if not detected
    """
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext)


def detect_language_from_filename(file_path: str) -> Optional[str]:
    """
    Detect programming language from filename.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or None if not detected
    """
    filename = os.path.basename(file_path)
    return FILENAME_TO_LANGUAGE.get(filename)


def detect_language_from_shebang(file_path: str) -> Optional[str]:
    """
    Detect programming language from shebang line.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name or None if not detected
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            
            # Check if it's a shebang line
            if first_line.startswith('#!'):
                # Extract the interpreter
                shebang = first_line[2:].strip()
                
                # Check for common patterns
                for pattern, language in SHEBANG_TO_LANGUAGE.items():
                    if pattern in shebang.lower():
                        return language
    except (IOError, OSError):
        pass
    
    return None


def detect_language(file_path: str) -> str:
    """
    Detect the programming language of a file.
    
    Tries multiple detection methods in order:
    1. Filename (for special files like Dockerfile)
    2. File extension
    3. Shebang line (for scripts)
    
    Args:
        file_path: Path to the file
        
    Returns:
        Language name, or 'unknown' if not detected
    """
    # Try filename first (highest priority)
    language = detect_language_from_filename(file_path)
    if language:
        return language
    
    # Try extension
    language = detect_language_from_extension(file_path)
    if language:
        return language
    
    # Try shebang for scripts without extension
    language = detect_language_from_shebang(file_path)
    if language:
        return language
    
    return 'unknown'


def get_language_category(language: str) -> str:
    """
    Get the category of a programming language.
    
    Args:
        language: Language name
        
    Returns:
        Category name (e.g., 'programming', 'markup', 'config', 'documentation')
    """
    programming_languages = {
        'python', 'javascript', 'typescript', 'java', 'c', 'cpp', 'csharp',
        'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r',
        'objective-c', 'dart', 'lua', 'perl', 'shell', 'bash', 'zsh',
        'fish', 'powershell', 'sql',
    }
    
    markup_languages = {
        'html', 'xml', 'markdown', 'restructuredtext', 'asciidoc',
    }
    
    style_languages = {
        'css', 'scss', 'sass', 'less',
    }
    
    config_languages = {
        'json', 'yaml', 'toml', 'ini', 'conf',
    }
    
    documentation_languages = {
        'text', 'markdown', 'restructuredtext', 'asciidoc',
    }
    
    if language in programming_languages:
        return 'programming'
    elif language in markup_languages:
        return 'markup'
    elif language in style_languages:
        return 'style'
    elif language in config_languages:
        return 'config'
    elif language in documentation_languages:
        return 'documentation'
    else:
        return 'other'


def is_supported_language(language: str) -> bool:
    """
    Check if a language is supported for indexing.
    
    Args:
        language: Language name
        
    Returns:
        True if the language is supported, False otherwise
    """
    # Support all detected languages except 'unknown'
    return language != 'unknown'


def get_supported_languages() -> List[str]:
    """
    Get a list of all supported programming languages.
    
    Returns:
        List of supported language names
    """
    return sorted(set(EXTENSION_TO_LANGUAGE.values()))


def get_language_extensions(language: str) -> List[str]:
    """
    Get all file extensions for a given language.
    
    Args:
        language: Language name
        
    Returns:
        List of file extensions (including the dot)
    """
    return [
        ext for ext, lang in EXTENSION_TO_LANGUAGE.items()
        if lang == language
    ]


def detect_languages_in_directory(directory: str) -> Dict[str, int]:
    """
    Detect all languages in a directory and count files per language.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Dictionary mapping language names to file counts
    """
    from .file_utils import walk_directory
    
    language_counts: Dict[str, int] = {}
    
    # Get all source files
    source_files = walk_directory(directory)
    
    # Count files per language
    for file_path in source_files:
        language = detect_language(file_path)
        language_counts[language] = language_counts.get(language, 0) + 1
    
    return language_counts
