"""
Unit tests for file reader.
"""

import os
import pytest
from pathlib import Path

from app.core.ingestion.file_reader import (
    FileInfo,
    FileReader,
    read_repository_files,
)


class TestFileInfo:
    """Tests for FileInfo dataclass."""
    
    def test_create_file_info(self, tmp_path):
        """Test creating FileInfo object."""
        file_path = tmp_path / 'test.py'
        file_path.write_text('print("hello")')
        
        file_info = FileInfo(
            absolute_path=str(file_path),
            relative_path='test.py',
            language='python',
            size_bytes=len('print("hello")'),
        )
        
        assert file_info.absolute_path == str(file_path)
        assert file_info.relative_path == 'test.py'
        assert file_info.language == 'python'
        assert file_info.size_bytes > 0
    
    def test_file_info_validation(self):
        """Test that FileInfo validates file existence."""
        with pytest.raises(ValueError):
            FileInfo(
                absolute_path='/nonexistent/file.py',
                relative_path='file.py',
                language='python',
                size_bytes=100,
            )


class TestFileReader:
    """Tests for FileReader class."""
    
    def test_init_with_valid_path(self, tmp_path):
        """Test initializing FileReader with valid path."""
        reader = FileReader(str(tmp_path))
        assert reader.repository_path == str(tmp_path.resolve())
    
    def test_init_with_invalid_path(self):
        """Test initializing FileReader with invalid path."""
        with pytest.raises(ValueError):
            FileReader('/nonexistent/path')
    
    def test_read_files_simple(self, tmp_path):
        """Test reading files from simple structure."""
        # Create test files
        (tmp_path / 'app.py').write_text('print("hello")')
        (tmp_path / 'utils.py').write_text('def helper(): pass')
        (tmp_path / 'README.md').write_text('# Project')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Check results
        assert len(file_infos) == 3
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'app.py' in file_names
        assert 'utils.py' in file_names
        assert 'README.md' in file_names
    
    def test_read_files_excludes_binary(self, tmp_path):
        """Test that binary files are excluded."""
        # Create test files
        (tmp_path / 'app.py').write_text('print("hello")')
        (tmp_path / 'image.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Check results
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'app.py' in file_names
        assert 'image.png' not in file_names
    
    def test_read_files_excludes_dependencies(self, tmp_path):
        """Test that dependency directories are excluded."""
        # Create structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'app.py').write_text('code')
        (tmp_path / 'node_modules').mkdir()
        (tmp_path / 'node_modules' / 'package.js').write_text('code')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Check results
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'app.py' in file_names
        assert 'package.js' not in file_names
    
    def test_read_files_respects_max_size(self, tmp_path):
        """Test that files exceeding max size are excluded."""
        # Create test files
        (tmp_path / 'small.py').write_text('x = 1')
        (tmp_path / 'large.py').write_text('x = 1' * 1000000)  # Large file
        
        # Read files with small max size
        reader = FileReader(str(tmp_path), max_file_size_mb=0.001)  # 1KB
        file_infos = reader.read_files()
        
        # Check results
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'small.py' in file_names
        assert 'large.py' not in file_names
    
    def test_read_files_detects_languages(self, tmp_path):
        """Test that languages are detected correctly."""
        # Create test files
        (tmp_path / 'app.py').write_text('print("hello")')
        (tmp_path / 'script.js').write_text('console.log("hello")')
        (tmp_path / 'Main.java').write_text('public class Main {}')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Check languages
        languages = {f.language for f in file_infos}
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'java' in languages
    
    def test_read_file_content(self, tmp_path):
        """Test reading file content."""
        # Create test file
        content = 'print("hello world")'
        (tmp_path / 'app.py').write_text(content)
        
        # Read content
        reader = FileReader(str(tmp_path))
        read_content = reader.read_file_content('app.py')
        
        assert read_content == content
    
    def test_read_file_content_absolute_path(self, tmp_path):
        """Test reading file content with absolute path."""
        # Create test file
        content = 'print("hello world")'
        file_path = tmp_path / 'app.py'
        file_path.write_text(content)
        
        # Read content
        reader = FileReader(str(tmp_path))
        read_content = reader.read_file_content(str(file_path))
        
        assert read_content == content
    
    def test_read_file_content_nonexistent(self, tmp_path):
        """Test reading nonexistent file."""
        reader = FileReader(str(tmp_path))
        
        with pytest.raises(ValueError):
            reader.read_file_content('nonexistent.py')
    
    def test_filter_by_language(self, tmp_path):
        """Test filtering files by language."""
        # Create test files
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / 'script.js').write_text('code')
        (tmp_path / 'Main.java').write_text('code')
        
        # Read files
        reader = FileReader(str(tmp_path))
        all_files = reader.read_files()
        
        # Filter by Python
        python_files = reader.filter_by_language(all_files, {'python'})
        assert len(python_files) == 1
        assert python_files[0].language == 'python'
        
        # Filter by JavaScript and Java
        js_java_files = reader.filter_by_language(all_files, {'javascript', 'java'})
        assert len(js_java_files) == 2
    
    def test_filter_by_path_pattern(self, tmp_path):
        """Test filtering files by path pattern."""
        # Create structure
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'app.py').write_text('code')
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'tests' / 'test_app.py').write_text('code')
        
        # Read files
        reader = FileReader(str(tmp_path))
        all_files = reader.read_files()
        
        # Include only src/
        src_files = reader.filter_by_path_pattern(all_files, include_patterns=['src/'])
        assert len(src_files) == 1
        assert 'src' in src_files[0].relative_path
        
        # Exclude tests/
        non_test_files = reader.filter_by_path_pattern(all_files, exclude_patterns=['tests/'])
        assert len(non_test_files) == 1
        assert 'tests' not in non_test_files[0].relative_path
    
    def test_get_total_size(self, tmp_path):
        """Test getting total size of files."""
        # Create test files
        (tmp_path / 'file1.py').write_text('x = 1')
        (tmp_path / 'file2.py').write_text('y = 2')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Get total size
        total_size = reader.get_total_size(file_infos)
        assert total_size > 0
        assert total_size == sum(f.size_bytes for f in file_infos)
    
    def test_get_file_count_by_language(self, tmp_path):
        """Test getting file count by language."""
        # Create test files
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / 'utils.py').write_text('code')
        (tmp_path / 'script.js').write_text('code')
        
        # Read files
        reader = FileReader(str(tmp_path))
        file_infos = reader.read_files()
        
        # Get counts
        counts = reader.get_file_count_by_language(file_infos)
        assert counts['python'] == 2
        assert counts['javascript'] == 1
    
    def test_get_language_statistics(self, tmp_path):
        """Test getting language statistics."""
        # Create test files
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / 'utils.py').write_text('code')
        (tmp_path / 'script.js').write_text('code')
        
        # Get statistics
        reader = FileReader(str(tmp_path))
        stats = reader.get_language_statistics()
        
        assert stats['python'] == 2
        assert stats['javascript'] == 1


class TestReadRepositoryFiles:
    """Tests for read_repository_files convenience function."""
    
    def test_read_repository_files(self, tmp_path):
        """Test reading repository files."""
        # Create test files
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / 'script.js').write_text('code')
        
        # Read files
        file_infos = read_repository_files(str(tmp_path))
        
        assert len(file_infos) == 2
    
    def test_read_repository_files_with_language_filter(self, tmp_path):
        """Test reading repository files with language filter."""
        # Create test files
        (tmp_path / 'app.py').write_text('code')
        (tmp_path / 'script.js').write_text('code')
        
        # Read only Python files
        file_infos = read_repository_files(str(tmp_path), languages={'python'})
        
        assert len(file_infos) == 1
        assert file_infos[0].language == 'python'
