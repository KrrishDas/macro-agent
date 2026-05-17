"""
tools/base.py
 
Defines the standard return contract for every tool in the system.
 
Every tool function should return a ToolResult. This keeps the executor
and loop simple — they never need to guess what a tool produced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class ToolResult:
    """
    The standard return type for all tools.
    
    Attributes:

        tool_name : str
        Name of the tool that produced this result.

        success : bool
        True if the tool ran without error.

        data : dict[str, Any]
        The tool's primary output payload. Structure varies per tool;
        each tool's docstring documents what keys it places here.

        error : str | None
        Error message if success is False, otherwise None.

        metadata : dict[str, Any]
        Supplementary info — series IDs used, date ranges, chart paths, etc.
        Kept separate from data so consumers can ignore it easily.
    """

    tool_name: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, 
           tool_name: str, 
           data: dict[str, Any], 
           metadata: dict[str, Any] | None = None,
           ) -> "ToolResult":
        """Return a successful ToolResult with the given data and metadata."""
        return cls(
            tool_name=tool_name,
            success=True,
            data=data,
            error=None,
            metadata=metadata or {}
        )
    
    @classmethod
    def fail(cls, tool_name: str, error: str) -> "ToolResult":
        """Return a failed ToolResult."""
        return cls(
            tool_name=tool_name,
            success=False,
            error=error,
        )
 
    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict (useful for JSON logging / report builder)."""
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    
    
