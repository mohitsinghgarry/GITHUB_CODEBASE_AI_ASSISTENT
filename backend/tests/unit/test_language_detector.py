"""
Unit tests for language detection utilities.
"""

import os
import tempfile
import pytest
from pathlib import Path

from app.utils.language_detector import (
    detect_language_from_extension,
    detect_language_from_filename,
    detect_language_from_shebang,
    detect_language,
    get_language_category,
    is_supported_language,
    get_supported_languages,
    get_language_extensions,
)


class TestDetectLanguageFromExtension:
    """Tests for detect_language_from_extension function."""
    
    def test_python_extension(self):
        """Test Python file extension detection."""
        assert detect_language_from_extension('script.py') == 'python'
        assert detect_language_from_extension('module.pyx') == 'python'
    
    def test_javascript_extension(self):
        """Test JavaScript file extension detection."""
        assert detect_language_from_extension('app.js') == 'javascript'
        assert detect_language_from_extension('component.jsx') == 'javascript'
    
    def test_typescript_extension(self):
        """Test TypeScript file extension detection."""
        assert detect_language_from_extension('app.ts') == 'typescript'
        assert detect_language_from_extension('component.tsx') == 'typescript'
    
    def test_java_extension(self):
        """Test Java file extension detection."""
        assert detect_language_from_extension('Main.java') == 'java'
    
    def test_cpp_extension(self):
        """Test C++ file extension detection."""
        assert detect_language_from_extension('main.cpp') == 'cpp'
        assert detect_language_from_extension('header.hpp') == 'cpp'
    
    def test_go_extension(self):
        """Test Go file extension detection."""
        assert detect_language_from_extension('main.go') == 'go'
    
    def test_rust_extension(self):
        """Test Rust file extension detection."""
        assert detect_language_from_extension('main.rs') == 'rust'
    
    def test_unknown_extension(self):
        """Test unknown file extension."""
        assert detect_language_from_extension('file.unknown') is None


class TestDetectLanguageFromFilename:
    """Tests for detect_language_from_filename function."""
    
    def test_dockerfile(self):
        """Test Dockerfile detection."""
        assert detect_language_from_filename('Dockerfile') == 'dockerfile'
        assert detect_language_from_filename('/path/to/Dockerfile') == 'dockerfile'
    
    def test_makefile(self):
        """Test Makefile detection."""
        assert detect_language_from_filename('Makefile') == 'makefile'
        assert detect_language_from_filename('/path/to/Makefile') == 'makefile'
    
    def test_gemfile(self):
        """Test Gemfile detection."""
        assert detect_language_from_filename('Gemfile') == 'ruby'
    
    def test_package_json(self):
        """Test package.json detection."""
        assert detect_language_from_filename('package.json') == 'json'
    
    def test_cargo_toml(self):
        """Test Cargo.toml detection."""
        assert detect_language_from_filename('Cargo.toml') == 'toml'
    
    def test_unknown_filename(self):
        """Test unknown filename."""
        assert detect_language_from_filename('unknown_file') is None


class TestDetectLanguageFromShebang:
    """Tests for detect_language_from_shebang function."""
    
    def test_python_shebang(self, tmp_path):
        """Test Python shebang detection."""
        file_path = tmp_path / 'script'
        file_path.write_text('#!/usr/bin/env python3\nprint("hello")')
        assert detect_language_from_shebang(str(file_path)) == 'python'
    
    def test_bash_shebang(self, tmp_path):
        """Test Bash shebang detection."""
        file_path = tmp_path / 'script'
        file_path.write_text('#!/bin/bash\necho "hello"')
        assert detect_language_from_shebang(str(file_path)) == 'bash'
    
    def test_node_shebang(self, tmp_path):
        """Test Node.js shebang detection."""
        file_path = tmp_path / 'script'
        file_path.write_text('#!/usr/bin/env node\nconsole.log("hello")')
        assert detect_language_from_shebang(str(file_path)) == 'javascript'
    
    def test_ruby_shebang(self, tmp_path):
        """Test Ruby shebang detection."""
        file_path = tmp_path / 'script'
        file_path.write_text('#!/usr/bin/env ruby\nputs "hello"')
        assert detect_language_from_shebang(str(file_path)) == 'ruby'
    
    def test_no_shebang(self, tmp_path):
        """Test file without shebang."""
        file_path = tmp_path / 'script'
        file_path.write_text('print("hello")')
        assert detect_language_from_shebang(str(file_path)) is None


class TestDetectLanguage:
    """Tests for detect_language function."""
    
    def test_detect_by_extension(self, tmp_path):
        """Test language detection by extension."""
        file_path = tmp_path / 'app.py'
        file_path.write_text('print("hello")')
        assert detect_language(str(file_path)) == 'python'
    
    def test_detect_by_filename(self, tmp_path):
        """Test language detection by filename."""
        file_path = tmp_path / 'Dockerfile'
        file_path.write_text('FROM python:3.9')
        assert detect_language(str(file_path)) == 'dockerfile'
    
    def test_detect_by_shebang(self, tmp_path):
        """Test language detection by shebang."""
        file_path = tmp_path / 'script'
        file_path.write_text('#!/usr/bin/env python3\nprint("hello")')
        assert detect_language(str(file_path)) == 'python'
    
    def test_filename_priority_over_extension(self, tmp_path):
        """Test that filename detection has priority over extension."""
        # Dockerfile might have .dockerfile extension, but filename should win
        file_path = tmp_path / 'Dockerfile'
        file_path.write_text('FROM python:3.9')
        assert detect_language(str(file_path)) == 'dockerfile'
    
    def test_unknown_file(self, tmp_path):
        """Test unknown file detection."""
        file_path = tmp_path / 'unknown'
        file_path.write_text('some content')
        assert detect_language(str(file_path)) == 'unknown'


class TestGetLanguageCategory:
    """Tests for get_language_category function."""
    
    def test_programming_languages(self):
        """Test programming language category."""
        assert get_language_category('python') == 'programming'
        assert get_language_category('javascript') == 'programming'
        assert get_language_category('java') == 'programming'
    
    def test_markup_languages(self):
        """Test markup language category."""
        assert get_language_category('html') == 'markup'
        assert get_language_category('xml') == 'markup'
        assert get_language_category('markdown') == 'markup'
    
    def test_style_languages(self):
        """Test style language category."""
        assert get_language_category('css') == 'style'
        assert get_language_category('scss') == 'style'
    
    def test_config_languages(self):
        """Test config language category."""
        assert get_language_category('json') == 'config'
        assert get_language_category('yaml') == 'config'
        assert get_language_category('toml') == 'config'
    
    def test_documentation_languages(self):
        """Test documentation language category."""
        assert get_language_category('text') == 'documentation'
        assert get_language_category('markdown') in ['markup', 'documentation']
    
    def test_other_category(self):
        """Test other category."""
        assert get_language_category('unknown') == 'other'


class TestIsSupportedLanguage:
    """Tests for is_supported_language function."""
    
    def test_supported_languages(self):
        """Test that known languages are supported."""
        assert is_supported_language('python')
        assert is_supported_language('javascript')
        assert is_supported_language('java')
    
    def test_unknown_not_supported(self):
        """Test that unknown language is not supported."""
        assert not is_supported_language('unknown')


class TestGetSupportedLanguages:
    """Tests for get_supported_languages function."""
    
    def test_returns_list(self):
        """Test that function returns a list."""
        languages = get_supported_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0
    
    def test_contains_common_languages(self):
        """Test that list contains common languages."""
        languages = get_supported_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'java' in languages
        assert 'cpp' in languages
    
    def test_sorted(self):
        """Test that list is sorted."""
        languages = get_supported_languages()
        assert languages == sorted(languages)


class TestGetLanguageExtensions:
    """Tests for get_language_extensions function."""
    
    def test_python_extensions(self):
        """Test Python extensions."""
        extensions = get_language_extensions('python')
        assert '.py' in extensions
        assert '.pyx' in extensions
    
    def test_javascript_extensions(self):
        """Test JavaScript extensions."""
        extensions = get_language_extensions('javascript')
        assert '.js' in extensions
        assert '.jsx' in extensions
    
    def test_typescript_extensions(self):
        """Test TypeScript extensions."""
        extensions = get_language_extensions('typescript')
        assert '.ts' in extensions
        assert '.tsx' in extensions
    
    def test_unknown_language(self):
        """Test unknown language returns empty list."""
        extensions = get_language_extensions('unknown_language')
        assert extensions == []


class TestLanguageDetectionConsistency:
    """Tests for language detection consistency."""
    
    def test_same_language_for_all_extensions(self, tmp_path):
        """Test that all extensions for a language are detected correctly."""
        # Python extensions
        python_extensions = ['.py', '.pyx', '.pyi']
        for ext in python_extensions:
            file_path = tmp_path / f'test{ext}'
            file_path.write_text('# Python code')
            assert detect_language(str(file_path)) == 'python'
    
    def test_case_insensitive_extension(self, tmp_path):
        """Test that extension detection is case-insensitive."""
        file_path = tmp_path / 'test.PY'
        file_path.write_text('# Python code')
        assert detect_language(str(file_path)) == 'python'
