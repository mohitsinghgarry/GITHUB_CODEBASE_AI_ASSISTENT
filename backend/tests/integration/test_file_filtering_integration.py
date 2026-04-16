"""
Integration tests for file filtering workflow.

Tests the complete workflow of reading a repository, filtering files,
and detecting languages.
"""

import os
import pytest
from pathlib import Path

from app.core.ingestion.file_reader import FileReader, read_repository_files


class TestFileFilteringIntegration:
    """Integration tests for file filtering."""
    
    @pytest.fixture
    def sample_repo(self, tmp_path):
        """Create a sample repository structure."""
        # Source files
        (tmp_path / 'src').mkdir()
        (tmp_path / 'src' / 'main.py').write_text('def main(): pass')
        (tmp_path / 'src' / 'utils.py').write_text('def helper(): pass')
        (tmp_path / 'src' / 'app.js').write_text('console.log("hello")')
        
        # Tests
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'tests' / 'test_main.py').write_text('def test_main(): pass')
        
        # Config files
        (tmp_path / 'package.json').write_text('{"name": "test"}')
        (tmp_path / 'README.md').write_text('# Test Project')
        
        # Binary files (should be excluded)
        (tmp_path / 'image.png').write_bytes(b'\x89PNG\r\n\x1a\n')
        (tmp_path / 'video.mp4').write_bytes(b'binary video data')
        
        # Dependencies (should be excluded)
        (tmp_path / 'node_modules').mkdir()
        (tmp_path / 'node_modules' / 'package.js').write_text('module.exports = {}')
        
        # Build artifacts (should be excluded)
        (tmp_path / 'dist').mkdir()
        (tmp_path / 'dist' / 'bundle.js').write_text('// minified code')
        
        # Python cache (should be excluded)
        (tmp_path / '__pycache__').mkdir()
        (tmp_path / '__pycache__' / 'main.cpython-39.pyc').write_bytes(b'bytecode')
        
        # Lock files (should be excluded)
        (tmp_path / 'package-lock.json').write_text('{}')
        
        return tmp_path
    
    def test_read_repository_filters_correctly(self, sample_repo):
        """Test that repository reading filters files correctly."""
        reader = FileReader(str(sample_repo))
        file_infos = reader.read_files()
        
        # Get file names
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        
        # Should include source files
        assert 'main.py' in file_names
        assert 'utils.py' in file_names
        assert 'app.js' in file_names
        assert 'test_main.py' in file_names
        assert 'package.json' in file_names
        assert 'README.md' in file_names
        
        # Should exclude binary files
        assert 'image.png' not in file_names
        assert 'video.mp4' not in file_names
        
        # Should exclude dependencies
        assert 'package.js' not in file_names  # from node_modules
        
        # Should exclude build artifacts
        assert 'bundle.js' not in file_names  # from dist
        
        # Should exclude Python cache
        assert 'main.cpython-39.pyc' not in file_names
        
        # Should exclude lock files
        assert 'package-lock.json' not in file_names
    
    def test_language_detection_integration(self, sample_repo):
        """Test that languages are detected correctly."""
        reader = FileReader(str(sample_repo))
        file_infos = reader.read_files()
        
        # Get language counts
        language_counts = reader.get_file_count_by_language(file_infos)
        
        # Should detect Python files
        assert language_counts.get('python', 0) == 3  # main.py, utils.py, test_main.py
        
        # Should detect JavaScript files
        assert language_counts.get('javascript', 0) == 1  # app.js
        
        # Should detect JSON files
        assert language_counts.get('json', 0) == 1  # package.json
        
        # Should detect Markdown files
        assert language_counts.get('markdown', 0) == 1  # README.md
    
    def test_filter_by_language(self, sample_repo):
        """Test filtering files by language."""
        reader = FileReader(str(sample_repo))
        all_files = reader.read_files()
        
        # Filter Python files only
        python_files = reader.filter_by_language(all_files, {'python'})
        assert len(python_files) == 3
        assert all(f.language == 'python' for f in python_files)
        
        # Filter JavaScript files only
        js_files = reader.filter_by_language(all_files, {'javascript'})
        assert len(js_files) == 1
        assert all(f.language == 'javascript' for f in js_files)
    
    def test_filter_by_path_pattern(self, sample_repo):
        """Test filtering files by path pattern."""
        reader = FileReader(str(sample_repo))
        all_files = reader.read_files()
        
        # Include only src/ directory
        src_files = reader.filter_by_path_pattern(all_files, include_patterns=['src/'])
        assert len(src_files) == 3  # main.py, utils.py, app.js
        assert all('src' in f.relative_path for f in src_files)
        
        # Exclude tests/ directory
        non_test_files = reader.filter_by_path_pattern(all_files, exclude_patterns=['tests/'])
        test_files = [f for f in all_files if 'tests' in f.relative_path]
        assert len(non_test_files) == len(all_files) - len(test_files)
    
    def test_get_language_statistics(self, sample_repo):
        """Test getting language statistics."""
        reader = FileReader(str(sample_repo))
        stats = reader.get_language_statistics()
        
        # Should have statistics for all languages
        assert stats.get('python', 0) >= 3
        assert stats.get('javascript', 0) >= 1
        assert stats.get('json', 0) >= 1
        assert stats.get('markdown', 0) >= 1
    
    def test_convenience_function(self, sample_repo):
        """Test the convenience function for reading repository files."""
        # Read all files
        all_files = read_repository_files(str(sample_repo))
        assert len(all_files) > 0
        
        # Read only Python files
        python_files = read_repository_files(str(sample_repo), languages={'python'})
        assert len(python_files) == 3
        assert all(f.language == 'python' for f in python_files)
    
    def test_max_file_size_limit(self, tmp_path):
        """Test that files exceeding max size are excluded."""
        # Create small and large files
        (tmp_path / 'small.py').write_text('x = 1')
        (tmp_path / 'large.py').write_text('x = 1\n' * 100000)  # Large file
        
        # Read with small max size
        reader = FileReader(str(tmp_path), max_file_size_mb=0.001)  # 1KB
        file_infos = reader.read_files()
        
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'small.py' in file_names
        assert 'large.py' not in file_names
    
    def test_read_file_content(self, sample_repo):
        """Test reading file content."""
        reader = FileReader(str(sample_repo))
        
        # Read content by relative path
        content = reader.read_file_content('src/main.py')
        assert 'def main()' in content
        
        # Read content by absolute path
        abs_path = os.path.join(str(sample_repo), 'src', 'utils.py')
        content = reader.read_file_content(abs_path)
        assert 'def helper()' in content
    
    def test_total_size_calculation(self, sample_repo):
        """Test calculating total size of files."""
        reader = FileReader(str(sample_repo))
        file_infos = reader.read_files()
        
        total_size = reader.get_total_size(file_infos)
        assert total_size > 0
        
        # Verify it matches sum of individual sizes
        expected_size = sum(f.size_bytes for f in file_infos)
        assert total_size == expected_size


class TestComplexRepositoryStructure:
    """Test file filtering with more complex repository structures."""
    
    @pytest.fixture
    def complex_repo(self, tmp_path):
        """Create a complex repository structure."""
        # Multi-level source structure
        (tmp_path / 'src' / 'api').mkdir(parents=True)
        (tmp_path / 'src' / 'api' / 'routes.py').write_text('# routes')
        (tmp_path / 'src' / 'api' / 'models.py').write_text('# models')
        
        (tmp_path / 'src' / 'utils').mkdir()
        (tmp_path / 'src' / 'utils' / 'helpers.py').write_text('# helpers')
        
        # Multiple test directories
        (tmp_path / 'tests' / 'unit').mkdir(parents=True)
        (tmp_path / 'tests' / 'unit' / 'test_api.py').write_text('# tests')
        
        (tmp_path / 'tests' / 'integration').mkdir()
        (tmp_path / 'tests' / 'integration' / 'test_e2e.py').write_text('# tests')
        
        # Multiple language files
        (tmp_path / 'frontend').mkdir()
        (tmp_path / 'frontend' / 'app.js').write_text('// js')
        (tmp_path / 'frontend' / 'app.ts').write_text('// ts')
        (tmp_path / 'frontend' / 'style.css').write_text('/* css */')
        
        # Hidden files
        (tmp_path / '.github').mkdir()
        (tmp_path / '.github' / 'workflows').mkdir()
        (tmp_path / '.github' / 'workflows' / 'ci.yml').write_text('# ci')
        
        return tmp_path
    
    def test_complex_structure_filtering(self, complex_repo):
        """Test filtering in complex repository structure."""
        reader = FileReader(str(complex_repo))
        file_infos = reader.read_files()
        
        # Should find all source files
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'routes.py' in file_names
        assert 'models.py' in file_names
        assert 'helpers.py' in file_names
        assert 'test_api.py' in file_names
        assert 'test_e2e.py' in file_names
        assert 'app.js' in file_names
        assert 'app.ts' in file_names
        assert 'style.css' in file_names
        
        # Should not include hidden files by default
        assert 'ci.yml' not in file_names
    
    def test_include_hidden_files(self, complex_repo):
        """Test including hidden files."""
        reader = FileReader(str(complex_repo), include_hidden=True)
        file_infos = reader.read_files()
        
        file_names = [os.path.basename(f.absolute_path) for f in file_infos]
        assert 'ci.yml' in file_names
    
    def test_multi_language_detection(self, complex_repo):
        """Test detecting multiple languages."""
        reader = FileReader(str(complex_repo))
        file_infos = reader.read_files()
        
        language_counts = reader.get_file_count_by_language(file_infos)
        
        assert language_counts.get('python', 0) >= 4
        assert language_counts.get('javascript', 0) >= 1
        assert language_counts.get('typescript', 0) >= 1
        assert language_counts.get('css', 0) >= 1
