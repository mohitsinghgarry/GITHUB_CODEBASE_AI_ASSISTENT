"""
Code chunking service with language-aware splitting.

This module provides intelligent code chunking that:
- Respects function and class boundaries
- Preserves file path, line numbers, and language metadata
- Supports configurable chunk size and overlap
- Falls back to character-based chunking when AST parsing fails

Requirements:
- 2.4: Split code files into chunks with configurable size limits
- 2.5: Preserve file path, line numbers, and language metadata for each chunk
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from ..core.config import Settings, get_settings
from ..utils.language_detector import detect_language


@dataclass
class CodeChunk:
    """
    Represents a chunk of code with metadata.
    
    Attributes:
        content: The actual code content
        file_path: Path to the source file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)
        language: Programming language of the code
        chunk_index: Index of this chunk within the file (0-indexed)
    """
    content: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    chunk_index: int
    
    def __post_init__(self):
        """Validate chunk data after initialization."""
        if self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line < self.start_line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= start_line ({self.start_line})"
            )
        if self.chunk_index < 0:
            raise ValueError(f"chunk_index must be >= 0, got {self.chunk_index}")
    
    def to_dict(self) -> dict:
        """Convert chunk to dictionary representation."""
        return {
            "content": self.content,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "language": self.language,
            "chunk_index": self.chunk_index,
        }


class ChunkingService:
    """
    Service for chunking code files with language-aware splitting.
    
    This service provides intelligent code chunking that attempts to respect
    function and class boundaries when possible, falling back to character-based
    chunking when necessary.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the chunking service.
        
        Args:
            settings: Application settings (uses global settings if not provided)
        """
        self.settings = settings or get_settings()
        self.chunk_size = self.settings.chunk_size
        self.chunk_overlap = self.settings.chunk_overlap
        self.max_chunk_size = self.settings.max_chunk_size
    
    def chunk_file(
        self,
        file_path: str,
        content: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[CodeChunk]:
        """
        Chunk a code file into smaller segments.
        
        Args:
            file_path: Path to the file being chunked
            content: File content (reads from file if not provided)
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap
            
        Returns:
            List of CodeChunk objects
            
        Raises:
            IOError: If file cannot be read
            ValueError: If chunk_size or chunk_overlap are invalid
        """
        # Read content if not provided
        if content is None:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # Use provided or default chunk parameters
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap
        
        # Validate parameters
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be > 0, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be >= 0, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be < chunk_size ({chunk_size})"
            )
        
        # Detect language
        language = detect_language(file_path)
        
        # Try language-aware chunking first
        chunks = self._chunk_language_aware(
            content, file_path, language, chunk_size, chunk_overlap
        )
        
        # Fall back to character-based chunking if language-aware fails
        if not chunks:
            chunks = self._chunk_character_based(
                content, file_path, language, chunk_size, chunk_overlap
            )
        
        return chunks
    
    def _chunk_language_aware(
        self,
        content: str,
        file_path: str,
        language: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[CodeChunk]:
        """
        Chunk code using language-aware splitting that respects boundaries.
        
        This method attempts to split code at natural boundaries like:
        - Function definitions
        - Class definitions
        - Method definitions
        - Top-level statements
        
        Args:
            content: File content
            file_path: Path to the file
            language: Programming language
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of CodeChunk objects, or empty list if parsing fails
        """
        # Get language-specific patterns
        patterns = self._get_boundary_patterns(language)
        if not patterns:
            return []
        
        # Split content into logical units
        units = self._split_into_units(content, patterns)
        if not units:
            return []
        
        # Group units into chunks
        chunks = self._group_units_into_chunks(
            units, file_path, language, chunk_size, chunk_overlap
        )
        
        return chunks
    
    def _chunk_character_based(
        self,
        content: str,
        file_path: str,
        language: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[CodeChunk]:
        """
        Chunk code using character-based splitting with line awareness.
        
        This is a fallback method that splits code by characters while
        trying to break at line boundaries when possible.
        
        Args:
            content: File content
            file_path: Path to the file
            language: Programming language
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of CodeChunk objects
        """
        if not content:
            return []
        
        lines = content.split('\n')
        chunks = []
        chunk_index = 0
        
        current_chunk_lines = []
        current_chunk_size = 0
        current_start_line = 1
        
        for line_num, line in enumerate(lines, start=1):
            line_with_newline = line + '\n' if line_num < len(lines) else line
            line_size = len(line_with_newline)
            
            # If adding this line would exceed chunk size and we have content
            if current_chunk_size + line_size > chunk_size and current_chunk_lines:
                # Create chunk from accumulated lines
                chunk_content = ''.join(current_chunk_lines).rstrip('\n')
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=current_start_line,
                    end_line=line_num - 1,
                    language=language,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1
                
                # Calculate overlap
                if chunk_overlap > 0:
                    # Keep last few lines for overlap
                    overlap_lines = []
                    overlap_size = 0
                    for prev_line in reversed(current_chunk_lines):
                        if overlap_size + len(prev_line) <= chunk_overlap:
                            overlap_lines.insert(0, prev_line)
                            overlap_size += len(prev_line)
                        else:
                            break
                    
                    # Start new chunk with overlap
                    current_chunk_lines = overlap_lines
                    current_chunk_size = overlap_size
                    # Calculate start line for overlap
                    overlap_line_count = len(overlap_lines)
                    current_start_line = line_num - overlap_line_count
                else:
                    current_chunk_lines = []
                    current_chunk_size = 0
                    current_start_line = line_num
            
            # Add current line to chunk
            current_chunk_lines.append(line_with_newline)
            current_chunk_size += line_size
        
        # Add final chunk if there's remaining content
        if current_chunk_lines:
            chunk_content = ''.join(current_chunk_lines).rstrip('\n')
            chunks.append(CodeChunk(
                content=chunk_content,
                file_path=file_path,
                start_line=current_start_line,
                end_line=len(lines),
                language=language,
                chunk_index=chunk_index,
            ))
        
        return chunks
    
    def _get_boundary_patterns(self, language: str) -> Optional[List[re.Pattern]]:
        """
        Get regex patterns for detecting code boundaries in a language.
        
        Args:
            language: Programming language
            
        Returns:
            List of compiled regex patterns, or None if language not supported
        """
        # Python patterns
        if language == 'python':
            return [
                re.compile(r'^(class\s+\w+.*?:)\s*$', re.MULTILINE),
                re.compile(r'^(def\s+\w+.*?:)\s*$', re.MULTILINE),
                re.compile(r'^(async\s+def\s+\w+.*?:)\s*$', re.MULTILINE),
            ]
        
        # JavaScript/TypeScript patterns
        elif language in ('javascript', 'typescript'):
            return [
                re.compile(r'^(class\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(function\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(async\s+function\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(const\s+\w+\s*=\s*\(.*?\)\s*=>\s*{)\s*$', re.MULTILINE),
                re.compile(r'^(export\s+(?:default\s+)?(?:class|function)\s+\w+.*?{)\s*$', re.MULTILINE),
            ]
        
        # Java patterns
        elif language == 'java':
            return [
                re.compile(r'^(\s*(?:public|private|protected)?\s*class\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(\s*(?:public|private|protected)?\s*interface\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+\w+\s*\(.*?\)\s*{)\s*$', re.MULTILINE),
            ]
        
        # C/C++ patterns
        elif language in ('c', 'cpp'):
            return [
                re.compile(r'^(class\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(struct\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(\w+\s+\w+\s*\(.*?\)\s*{)\s*$', re.MULTILINE),
            ]
        
        # Go patterns
        elif language == 'go':
            return [
                re.compile(r'^(type\s+\w+\s+struct\s*{)\s*$', re.MULTILINE),
                re.compile(r'^(type\s+\w+\s+interface\s*{)\s*$', re.MULTILINE),
                re.compile(r'^(func\s+(?:\(\w+\s+\*?\w+\)\s+)?\w+\s*\(.*?\).*?{)\s*$', re.MULTILINE),
            ]
        
        # Rust patterns
        elif language == 'rust':
            return [
                re.compile(r'^(struct\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(enum\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(trait\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(impl\s+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(fn\s+\w+.*?{)\s*$', re.MULTILINE),
            ]
        
        # Ruby patterns
        elif language == 'ruby':
            return [
                re.compile(r'^(class\s+\w+.*?)\s*$', re.MULTILINE),
                re.compile(r'^(module\s+\w+.*?)\s*$', re.MULTILINE),
                re.compile(r'^(def\s+\w+.*?)\s*$', re.MULTILINE),
            ]
        
        # PHP patterns
        elif language == 'php':
            return [
                re.compile(r'^(class\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(interface\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(trait\s+\w+.*?{)\s*$', re.MULTILINE),
                re.compile(r'^(function\s+\w+.*?{)\s*$', re.MULTILINE),
            ]
        
        # For unsupported languages, return None to trigger fallback
        return None
    
    def _split_into_units(
        self, content: str, patterns: List[re.Pattern]
    ) -> List[Tuple[str, int, int]]:
        """
        Split content into logical units based on boundary patterns.
        
        Args:
            content: File content
            patterns: List of regex patterns for boundaries
            
        Returns:
            List of tuples (unit_content, start_line, end_line)
        """
        lines = content.split('\n')
        units = []
        current_unit_lines = []
        current_start_line = 1
        
        for line_num, line in enumerate(lines, start=1):
            # Check if this line matches any boundary pattern
            is_boundary = any(pattern.match(line) for pattern in patterns)
            
            # If we hit a boundary and have accumulated content, save it
            if is_boundary and current_unit_lines:
                unit_content = '\n'.join(current_unit_lines)
                units.append((unit_content, current_start_line, line_num - 1))
                current_unit_lines = []
                current_start_line = line_num
            
            # Add line to current unit
            current_unit_lines.append(line)
        
        # Add final unit
        if current_unit_lines:
            unit_content = '\n'.join(current_unit_lines)
            units.append((unit_content, current_start_line, len(lines)))
        
        return units
    
    def _group_units_into_chunks(
        self,
        units: List[Tuple[str, int, int]],
        file_path: str,
        language: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[CodeChunk]:
        """
        Group logical units into chunks respecting size limits.
        
        Args:
            units: List of (content, start_line, end_line) tuples
            file_path: Path to the file
            language: Programming language
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of CodeChunk objects
        """
        chunks = []
        chunk_index = 0
        
        current_chunk_units = []
        current_chunk_size = 0
        
        for unit_content, start_line, end_line in units:
            unit_size = len(unit_content)
            
            # If this single unit exceeds max chunk size, split it
            if unit_size > self.max_chunk_size:
                # Save current chunk if any
                if current_chunk_units:
                    chunk_content = '\n'.join([u[0] for u in current_chunk_units])
                    chunk_start = current_chunk_units[0][1]
                    chunk_end = current_chunk_units[-1][2]
                    chunks.append(CodeChunk(
                        content=chunk_content,
                        file_path=file_path,
                        start_line=chunk_start,
                        end_line=chunk_end,
                        language=language,
                        chunk_index=chunk_index,
                    ))
                    chunk_index += 1
                    current_chunk_units = []
                    current_chunk_size = 0
                
                # Split large unit using character-based chunking
                large_unit_chunks = self._chunk_character_based(
                    unit_content, file_path, language, chunk_size, chunk_overlap
                )
                # Adjust line numbers
                for luc in large_unit_chunks:
                    luc.start_line += start_line - 1
                    luc.end_line += start_line - 1
                    luc.chunk_index = chunk_index
                    chunks.append(luc)
                    chunk_index += 1
                continue
            
            # If adding this unit would exceed chunk size
            if current_chunk_size + unit_size > chunk_size and current_chunk_units:
                # Save current chunk
                chunk_content = '\n'.join([u[0] for u in current_chunk_units])
                chunk_start = current_chunk_units[0][1]
                chunk_end = current_chunk_units[-1][2]
                chunks.append(CodeChunk(
                    content=chunk_content,
                    file_path=file_path,
                    start_line=chunk_start,
                    end_line=chunk_end,
                    language=language,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1
                
                # Handle overlap
                if chunk_overlap > 0:
                    # Keep last few units for overlap
                    overlap_units = []
                    overlap_size = 0
                    for prev_unit in reversed(current_chunk_units):
                        if overlap_size + len(prev_unit[0]) <= chunk_overlap:
                            overlap_units.insert(0, prev_unit)
                            overlap_size += len(prev_unit[0])
                        else:
                            break
                    current_chunk_units = overlap_units
                    current_chunk_size = overlap_size
                else:
                    current_chunk_units = []
                    current_chunk_size = 0
            
            # Add unit to current chunk
            current_chunk_units.append((unit_content, start_line, end_line))
            current_chunk_size += unit_size + 1  # +1 for newline
        
        # Add final chunk
        if current_chunk_units:
            chunk_content = '\n'.join([u[0] for u in current_chunk_units])
            chunk_start = current_chunk_units[0][1]
            chunk_end = current_chunk_units[-1][2]
            chunks.append(CodeChunk(
                content=chunk_content,
                file_path=file_path,
                start_line=chunk_start,
                end_line=chunk_end,
                language=language,
                chunk_index=chunk_index,
            ))
        
        return chunks
    
    def chunk_multiple_files(
        self,
        file_paths: List[str],
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[CodeChunk]:
        """
        Chunk multiple files in batch.
        
        Args:
            file_paths: List of file paths to chunk
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap
            
        Returns:
            List of CodeChunk objects from all files
        """
        all_chunks = []
        
        for file_path in file_paths:
            try:
                chunks = self.chunk_file(file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                all_chunks.extend(chunks)
            except Exception as e:
                # Log error but continue with other files
                print(f"Error chunking file {file_path}: {e}")
                continue
        
        return all_chunks


# Convenience function for quick chunking
def chunk_code_file(
    file_path: str,
    content: Optional[str] = None,
    chunk_size: int = 512,
    chunk_overlap: int = 50,
) -> List[CodeChunk]:
    """
    Convenience function to chunk a single code file.
    
    Args:
        file_path: Path to the file
        content: File content (reads from file if not provided)
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of CodeChunk objects
    """
    service = ChunkingService()
    return service.chunk_file(
        file_path=file_path,
        content=content,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
