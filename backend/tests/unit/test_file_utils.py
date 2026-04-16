"""
Unit tests for file utility functions.
"""

import os
import tempfile
import pytest
from pathlib import Path

from app.utils.file_utils import (
    is_binary_file,
    should_exclude_directory,
    should_exclude_file,
    is_source_code_file,
    filter_files,
    walk_directory,
    get_file_size,
    get_relative_path,
)


class TestIsBinaryFile:
    """Tests for is_binary_file function."""
    
    def test_binary_by_extension(self, tmp_path):
        """Test binary detection by file extension."""
        # Create test files
        binary_files = [
            'image.png', 'video.mp4', 'archive.zip', 'executable.exe',
            'document.pdf', 'font.ttf', 'database.db'
        ]
        
        for filename in binary_files:
            file_path = tmp_path / filename
            file_path.write_bytes(b'binary content')
            assert is_binary_file(str(file_path)), f"{filename} should be detected as binary"
    
    def test_text_by_extension(self, tmp_path):
        """Test text file detection by extension."""
        text_files = [
            'script.py', 'code.js', 'style.css', 'config.json',
            'readme.md', 'data.txt'
        ]
        
        for filename in text_files:
            file_path = tmp_path / filename
            file_path.write_text('text content')
            assert not is_binary_file(str(file_path)), f"{filename} should not be detected as binary"
    
    def test_binary_by_content(self, tmp_path):
        """Test binary detection by file content (null bytes)."""
        file_path = tmp_path / 'unknown_file'
        file_path.write_bytes(b'text\x00binary')
        assert is_binary_file(str(file_path))
    
    def test_text_by_content(self, tmp_path):
        """Test text file detection by content."""
        file_path = tmp_path / 'unknown_file'
        file_path.write_text('This is plain text content')
        assert not is_binary_file(str(file_path))


class TestShouldExcludeDirectory:
    """Tests for should_exclude_directory function."""
    
    def test_exclude_node_modules(self):
        """Test that node_modules is excluded."""
        assert should_exclude_directory('node_modules')
    
    def test_exclude_venv(self):
        """Test that venv is excluded."""
        assert should_exclude_directory('venv')
        assert should_exclude_directory('.venv')
    
    def test_exclude_pycache(self):
        """Test that __pycache__ is excluded."""
        assert should_exclude_directory('__pycache__')
    
    def test_exclude_git(self):
        """Test that .git is excluded."""
        assert should_exclude_directory('.git')
    
    def test_exclude_build_dirs(self):
        """Test that build directories are excluded."""
        assert should_exclude_directory('build')
        assert should_exclude_directory('dist')
        assert should_exclude_directory('target')
    
    def test_include_source_dirs(self):
        """Test that source directories are not excluded."""
        assert not should_exclude_directory('src')
        assert not should_exclude_directory('lib')
        assert not should_exclude_directory('app')


class TestShouldExcludeFile:
    """Tests for should_exclude_file function."""
    
    def test_exclude_lock_files(self):
        """Test that lock files are excluded."""
        assert should_exclude_file('package-lock.json')
        assert should_exclude_file('yarn.lock')
        assert should_exclude_file('Pipfile.lock')
    
    def test_exclude_minified_files(self):
        """Test that minified files are excluded."""
        assert should_exclude_file('app.min.js')
        assert should_exclude_file('style.min.css')
    
    def test_exclude_env_files(self):
        """Test that environment files are excluded."""
        assert should_exclude_file('.env')
        assert should_exclude_file('.env.local')
    
    def test_include_source_files(self):
        """Test that source files are not excluded."""
        assert not should_exclude_file('app.py')
        assert not should_exclude_file('index.js')
        assert not should_exclude_file('style.css')


class TestIsSourceCodeFile:
    """Tests for is_source_code_file function."""
    
    def test_python_files(self, tmp_path):
        """Test Python file detection."""
        file_path = tmp_path / 'script.py'
        file_path.write_text('print("hello")')
        assert is_source_code_file(str(file_path))
    
    def test_javascript_files(self, tmp_path):
        """Test JavaScript file detection."""
        file_path = tmp_path / 'app.js'
        file_path.write_text('console.log("hello")')
        assert is_source_code_file(str(file_path))
    
    def test_binary_files_excluded(self, tmp_path):
        """Test that binary files are not considered source code."""
        file_path = tmp_path / 'image.png'
        file_path.write_bytes(b'\x89PNG\r\n\x1a\n')
        assert not is_source_code_file(str(file_path))
    
    def test_excluded_files(self, tmp_path):
        """Test that excluded files are not considered source code."""
        file_path = tmp_path / 'package-lock.json'
        file_path.write_text('{}')
        assert not is_source_code_file(str(file_path))


class TestFilterFiles:
    """Tests for filter_files function."""
    
    def test_filter_mixed_files(self, tmp_path):
        """Test filtering a mix of source and non-source files."""
        # Create test files
        files = {
            'app.py': 'source',
            'script.js': 'source',
            'image.png': 'binary',
            'package-lock.json': 'excluded',
            'README.md': 'source',
        }
        
        file_paths = []
        for filename, file_type in files.items():
            file_path = tmp_path / filename
            if file_type == 'binary':
                file_path.write_bytes(b'binary')
            else:
                file_path.write_text('content')
            file_paths.append(str(file_path))
        
        # Filter files
        filtered = filter_files(file_paths)
        
        # Check results
        filtered_names = [os.path.basename(f) for f in filtered]
        assert 'app.py' in filtered_names
        assert 'script.js' in filtered_names
        assert 'README.md' in filtered_names
        assert 'image.png' not in filtered_names
        assert 'package-lock.json' not in filtered_names


class TestWalkDirectory:
    """Tests for walk_directory function."""
    
    def test_walk_simple_structure(self, tmp_path):
        """Test walking a simple directory structure."""
        # Create structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'app.py').write_text('code')
        (tmp_path / 'src' / 'utils.py').write_text('code')
        (tmp_path / 'README.md').write_text('docs')
        
        # Walk directory
        files = walk_directory(str(tmp_path))
        
        # Check results
        assert len(files) == 3
        file_names = [os.path.basename(f) for f in files]
        assert 'app.py' in file_names
        assert 'utils.py' in file_names
        assert 'README.md' in file_names
    
    def test_walk_excludes_node_modules(self, tmp_path):
        """Test that node_modules is excluded."""
        # Create structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'app.js').write_text('code')
        (tmp_path / 'node_modules').mkdir()
        (tmp_path / 'node_modules' / 'package.js').write_text('code')
        
        # Walk directory
        files = walk_directory(str(tmp_path))
        
        # Check results
        file_names = [os.path.basename(f) for f in files]
        assert 'app.js' in file_names
        assert 'package.js' not in file_names
    
    def test_walk_excludes_pycache(self, tmp_path):
        """Test that __pycache__ is excluded."""
        # Create structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'app.py').write_text('code')
        (tmp_path / 'src' / '__pycache__').mkdir()
        (tmp_path / 'src' / '__pycache__' / 'app.cpython-39.pyc').write_bytes(b'bytecode')
        
        # Walk directory
        files = walk_directory(str(tmp_path))
        
        # Check results
        file_names = [os.path.basename(f) for f in files]
        assert 'app.py' in file_names
        assert 'app.cpython-39.pyc' not in file_names
    
    def test_walk_excludes_hidden_by_default(self, tmp_path):
        """Test that hidden files are excluded by default."""
        # Create structure
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / '.hidden.py').write_text('code')
        (tmp_path / '.hidden_dir').mkdir()
        (tmp_path / '.hidden_dir' / 'file.py').write_text('code')
        
        # Walk directory (default: exclude hidden)
        files = walk_directory(str(tmp_path), include_hidden=False)
        
        # Check results
        file_names = [os.path.basename(f) for f in files]
        assert 'app.py' in file_names
        assert '.hidden.py' not in file_names
        assert 'file.py' not in file_names
    
    def test_walk_includes_hidden_when_requested(self, tmp_path):
        """Test that hidden files are included when requested."""
        # Create structure
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / '.hidden.py').write_text('code')
        
        # Walk directory (include hidden)
        files = walk_directory(str(tmp_path), include_hidden=True)
        
        # Check results
        file_names = [os.path.basename(f) for f in files]
        assert 'app.py' in file_names
        assert '.hidden.py' in file_names


class TestGetFileSize:
    """Tests for get_file_size function."""
    
    def test_get_size_of_existing_file(self, tmp_path):
        """Test getting size of an existing file."""
        file_path = tmp_path / 'test.txt'
        content = 'Hello, World!'
        file_path.write_text(content)
        
        size = get_file_size(str(file_path))
        assert size == len(content.encode('utf-8'))
    
    def test_get_size_of_nonexistent_file(self):
        """Test getting size of a nonexistent file."""
        size = get_file_size('/nonexistent/file.txt')
        assert size == 0


class TestGetRelativePath:
    """Tests for get_relative_path function."""
    
    def test_get_relative_path(self, tmp_path):
        """Test getting relative path."""
        root = str(tmp_path)
        file_path = str(tmp_path / 'src' / 'app.py')
        
        relative = get_relative_path(file_path, root)
        assert relative == os.path.join('src', 'app.py')
    
    def test_get_relative_path_same_dir(self, tmp_path):
        """Test getting relative path in same directory."""
        root = str(tmp_path)
        file_path = str(tmp_path / 'app.py')
        
        relative = get_relative_path(file_path, root)
        assert relative == 'app.py'
