"""Controlled assistant-name normalization for spoken command routing."""

from __future__ import annotations

from dataclasses import dataclass
import re


CANONICAL_ASSISTANT_NAME = "astra"

# Keep this list deliberately small. These are observed speech-recognition
# variants, not unrestricted fuzzy matches.
ASSISTANT_NAME_ALIASES = (
    "astra",
    "ashtra",
    "ashram",
    "jarvis",
)

_INVOCATION_PATTERN = re.compile(
    r"^(?:(?:hey|hello)\s+)?"
    r"(?P<alias>astra|ashtra|jarvis)"
    r"(?=$|[\s,:;.!?])"
    r"(?P<command>.*)$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AssistantInvocation:
    alias: str
    command: str


def normalize_assistant_invocation(text: str | None) -> AssistantInvocation | None:
    """Extract a leading assistant invocation using only known aliases."""

    if text is None:
        return None

    normalized = " ".join(str(text).strip().split())
    match = _INVOCATION_PATTERN.match(normalized)

    if not match:
        return None

    command = match.group("command").lstrip(" \t,:;.!?").strip()

    return AssistantInvocation(
        alias=match.group("alias").lower(),
        command=command,
    )
