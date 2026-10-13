"""MCP tools for reading company announcement files."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


SCRIPT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(SCRIPT_ROOT / ".env")
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(SCRIPT_ROOT))).expanduser()
mcp = FastMCP("FilesystemMCPServer")


class FilesystemMCPServer:
    """Read-only access to files inside the configured announcements directory."""

    def __init__(self, announcements_path: str | os.PathLike[str] | None = None):
        configured_path = announcements_path or os.getenv(
            "ANNOUNCEMENTS_PATH", "data/announcements"
        )
        path = Path(configured_path).expanduser()
        self.announcements_path = (
            path if path.is_absolute() else PROJECT_ROOT / path
        ).resolve()
        if not self.announcements_path.is_dir():
            raise FileNotFoundError(
                f"Announcements directory not found: {self.announcements_path}"
            )

    def _resolve_file(self, filename: str) -> Path:
        candidate = (self.announcements_path / filename).resolve()
        if not candidate.is_relative_to(self.announcements_path):
            raise ValueError("Filename must refer to a file inside the announcements directory")
        return candidate

    def list_announcements(self) -> dict[str, Any]:
        files = []
        for path in self.announcements_path.iterdir():
            if path.is_file():
                stat = path.stat()
                files.append({
                    "filename": path.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(
                        sep=" ", timespec="seconds"
                    ),
                })
        files.sort(key=lambda item: item["modified"], reverse=True)
        return {"announcements": files, "count": len(files)}

    def read_announcement(self, filename: str) -> dict[str, Any]:
        path = self._resolve_file(filename)
        if not path.is_file():
            return {
                "filename": filename,
                "found": False,
                "message": f"Announcement '{filename}' not found",
            }
        stat = path.stat()
        return {
            "filename": path.name,
            "content": path.read_text(encoding="utf-8"),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(
                sep=" ", timespec="seconds"
            ),
            "size": stat.st_size,
            "found": True,
        }

    def get_recent_announcements(self, limit: int = 3) -> dict[str, Any]:
        if limit < 0:
            raise ValueError("limit must be zero or greater")
        recent = self.list_announcements()["announcements"][:limit]
        announcements = [
            result
            for item in recent
            if (result := self.read_announcement(item["filename"])).get("found")
        ]
        return {"announcements": announcements, "count": len(announcements)}

    def search_announcements(self, keyword: str) -> dict[str, Any]:
        if not keyword.strip():
            raise ValueError("keyword must not be empty")
        term = keyword.casefold()
        matches = []
        for item in self.list_announcements()["announcements"]:
            result = self.read_announcement(item["filename"])
            if result.get("found") and (
                term in item["filename"].casefold()
                or term in result["content"].casefold()
            ):
                matches.append(result)
        return {"keyword": keyword, "matches": matches, "count": len(matches)}


_server: FilesystemMCPServer | None = None


def _filesystem() -> FilesystemMCPServer:
    global _server
    if _server is None:
        _server = FilesystemMCPServer()
    return _server


@mcp.tool()
def list_announcements() -> dict[str, Any]:
    """List announcement filenames, sizes, and modification times."""
    return _filesystem().list_announcements()


@mcp.tool()
def read_announcement(filename: str) -> dict[str, Any]:
    """Read an announcement file by filename."""
    return _filesystem().read_announcement(filename)


@mcp.tool()
def get_recent_announcements(limit: int = 3) -> dict[str, Any]:
    """Read the most recently modified announcements."""
    return _filesystem().get_recent_announcements(limit)


@mcp.tool()
def search_announcements(keyword: str) -> dict[str, Any]:
    """Search announcement filenames and contents for a keyword."""
    return _filesystem().search_announcements(keyword)


if __name__ == "__main__":
    mcp.run(transport="stdio")
