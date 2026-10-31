"""Safe, deterministic ROSA conversation and command-routing core.

The engine never executes device actions itself. It returns typed action proposals
for the Android bridge to validate and request confirmation for.
"""
from dataclasses import dataclass, field
from typing import Any
import re

@dataclass(frozen=True)
class Action:
    kind: str
    arguments: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = True

@dataclass(frozen=True)
class AssistantReply:
    text: str
    intent: str = "chat"
    action: Action | None = None
    needs_clarification: bool = False

class RosaEngine:
    """Small offline-first intent engine; online LLM is an optional later adapter."""

    def respond(self, text: str, language: str = "en") -> AssistantReply:
        raw = (text or "").strip()
        if not raw:
            return AssistantReply("I didn't hear that. Please try again.", needs_clarification=True)

        normalized = re.sub(r"\s+", " ", raw.casefold()).strip()

        # Explicit, predictable device intents. Never claim an action was completed.
        if any(x in normalized for x in ("open settings", "settings open", "సెట్టింగ్స్ ఓపెన్")):
            return AssistantReply("I can open Android Settings. Shall I continue?",
                                  "open_settings", Action("open_settings", {}, True))
        if any(x in normalized for x in ("set an alarm", "set alarm", "alarm for", "అలారం పెట్టు")):
            match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", normalized)
            if not match:
                return AssistantReply("What time should I set the alarm for?",
                                      "set_alarm", needs_clarification=True)
            hour = int(match.group(1)); minute = int(match.group(2) or 0)
            meridiem = match.group(3)
            if minute > 59 or hour < 1 or hour > 12:
                return AssistantReply("Please tell me a valid time, like 7:30 AM.",
                                      "set_alarm", needs_clarification=True)
            if meridiem == "pm" and hour != 12: hour += 12
            if meridiem == "am" and hour == 12: hour = 0
            return AssistantReply(f"Set an alarm for {hour:02d}:{minute:02d}?",
                                  "set_alarm", Action("set_alarm", {"hour": hour, "minute": minute}, True))
        if any(x in normalized for x in ("what time", "current time", "time now", "ఇప్పుడు టైమ్")):
            return AssistantReply("I can read the current device time.", "get_time",
                                  Action("get_time", {}, False))
        if any(x in normalized for x in ("who are you", "your name", "నీ పేరు")):
            return AssistantReply("I'm ROSA — your voice-first personal assistant.")
        return AssistantReply(
            "I’m listening. I can help with supported phone commands, or answer through the online AI service when it’s connected.",
            "chat",
        )
