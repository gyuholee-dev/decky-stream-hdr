"""Errors the panel can show. Each carries a stable code so the frontend can translate it.

The message stays English: it is what goes to the log. The frontend never shows it directly.
"""
from __future__ import annotations

from typing import Optional


class CodedError(Exception):
    def __init__(self, code: str, message: str, detail: Optional[str] = None):
        super().__init__(message)
        self.code = code
        self.detail = detail  # extra text that is not translatable (for example a tool's own output)

    def info(self) -> dict:
        return {"code": self.code, "detail": self.detail}


def info_for(code: str, detail: Optional[str] = None) -> dict:
    return {"code": code, "detail": detail}
