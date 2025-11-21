"""
File Tools for Vibe Agency (ARCH-027).

This module provides basic file system operations for agents:
- ReadFileTool: Read file contents
- WriteFileTool: Write content to files

Security:
- All operations go through ToolRegistry (governance gatekeeper)
- InvariantChecker validates paths before execution
- Soul rules prevent access to sensitive files (.git, kernel.py, etc.)

Design Principles:
- Simple, focused tools (one responsibility each)
- Structured error handling
- Clear success/failure reporting
- Path validation
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ReadFileTool:
    """
    Tool for reading file contents.

    Security:
    - Paths are validated by InvariantChecker before execution
    - Soul rules prevent reading sensitive files
    - Errors are logged and returned (no crashes)

    Example:
        >>> tool = ReadFileTool()
        >>> result = tool.execute(path="README.md")
        >>> print(result)
        {"content": "...", "path": "README.md", "size": 1234}
    """

    def execute(self, path: str, **kwargs) -> dict[str, Any]:
        """
        Read contents of a file.

        Args:
            path: File path to read
            **kwargs: Additional parameters (ignored, for extensibility)

        Returns:
            dict with keys:
                - content (str): File contents
                - path (str): Absolute path read
                - size (int): File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
            Exception: For other I/O errors

        Example:
            >>> tool = ReadFileTool()
            >>> result = tool.execute(path="config/soul.yaml")
            >>> print(result["content"][:50])
            name: "Vibe Guardian"
            version: "1.0"
        """
        try:
            file_path = Path(path)

            # Check existence
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            # Check if it's a file (not directory)
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {path}")

            # Read content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Get file size
            size = file_path.stat().st_size

            logger.info(f"📖 Read file: {file_path} ({size} bytes)")

            return {
                "content": content,
                "path": str(file_path.resolve()),
                "size": size,
            }

        except FileNotFoundError as e:
            logger.error(f"❌ File not found: {path}")
            raise

        except PermissionError as e:
            logger.error(f"❌ Permission denied: {path}")
            raise

        except Exception as e:
            logger.error(f"❌ Error reading file {path}: {e}")
            raise


class WriteFileTool:
    """
    Tool for writing content to files.

    Security:
    - Paths are validated by InvariantChecker before execution
    - Soul rules prevent writing to sensitive files (.git, kernel.py, etc.)
    - Creates parent directories if they don't exist
    - Errors are logged and returned (no crashes)

    Example:
        >>> tool = WriteFileTool()
        >>> result = tool.execute(path="test.txt", content="Hello, World!")
        >>> print(result)
        {"path": "/path/to/test.txt", "bytes_written": 13}
    """

    def execute(self, path: str, content: str, **kwargs) -> dict[str, Any]:
        """
        Write content to a file.

        Args:
            path: File path to write to
            content: Content to write (string)
            **kwargs: Additional parameters:
                - create_dirs (bool): Create parent dirs if missing (default: True)
                - encoding (str): File encoding (default: "utf-8")

        Returns:
            dict with keys:
                - path (str): Absolute path written
                - bytes_written (int): Number of bytes written

        Raises:
            PermissionError: If file can't be written
            Exception: For other I/O errors

        Example:
            >>> tool = WriteFileTool()
            >>> result = tool.execute(
            ...     path="docs/new_doc.md",
            ...     content="# New Document\\n\\nContent here."
            ... )
            >>> print(f"Wrote {result['bytes_written']} bytes")
            Wrote 34 bytes
        """
        try:
            file_path = Path(path)
            create_dirs = kwargs.get("create_dirs", True)
            encoding = kwargs.get("encoding", "utf-8")

            # Create parent directories if needed
            if create_dirs and not file_path.parent.exists():
                logger.debug(f"Creating parent directories: {file_path.parent}")
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            # Get size
            bytes_written = file_path.stat().st_size

            logger.info(f"✍️ Wrote file: {file_path} ({bytes_written} bytes)")

            return {
                "path": str(file_path.resolve()),
                "bytes_written": bytes_written,
            }

        except PermissionError as e:
            logger.error(f"❌ Permission denied: {path}")
            raise

        except Exception as e:
            logger.error(f"❌ Error writing file {path}: {e}")
            raise
