"""Python entry point called by the Android Compose application."""
import json
from rosa_core.engine import RosaEngine

_engine = RosaEngine()

def respond(message, language="en"):
    reply = _engine.respond(message, language)
    action = None
    if reply.action:
        action = {
            "kind": reply.action.kind,
            "arguments": reply.action.arguments,
            "requires_confirmation": reply.action.requires_confirmation,
        }
    return json.dumps({
        "text": reply.text,
        "intent": reply.intent,
        "needs_clarification": reply.needs_clarification,
        "action": action,
    }, ensure_ascii=False)
