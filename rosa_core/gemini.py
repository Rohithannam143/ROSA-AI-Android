"""Gemini REST adapter. API credentials are read only from server environment."""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

@dataclass
class GeminiError(Exception):
    message: str
    retryable: bool = False

class GeminiClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: float = 20.0):
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.timeout = timeout

    def generate(self, message: str, language: str = "auto", history: list[dict[str, str]] | None = None) -> str:
        if not self.api_key:
            raise GeminiError("Online AI is not configured yet. Add GEMINI_API_KEY on the backend.", False)
        if not message or not message.strip():
            raise GeminiError("Message cannot be empty.", False)

        lang_instruction = {
            "te": "Reply naturally in Telugu.",
            "hi": "Reply naturally in Hindi.",
            "en": "Reply naturally in English.",
            "auto": "Reply in the same language as the user's latest message (Telugu, Hindi, or English).",
        }.get(language, "Reply in the same language as the user's latest message.")
        system = (
            "You are ROSA, a concise, warm, capable personal Android assistant. "
            "Understand the user's intent before answering. Ask one clear question when details are missing. "
            "Never claim you changed phone settings, opened apps, sent messages, or completed actions; "
            "those actions must be performed and verified by the Android device layer. "
            "Do not invent device state. Keep answers useful and brief. " + lang_instruction
        )
        contents = []
        for item in (history or [])[-12:]:
            role = "model" if item.get("role") == "assistant" else "user"
            text = str(item.get("text", ""))[:3000]
            if text:
                contents.append({"role": role, "parts": [{"text": text}]})
        contents.append({"role": "user", "parts": [{"text": message[:6000]}]})
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.45, "maxOutputTokens": 700},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            candidates = data.get("candidates") or []
            parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
            answer = "".join(p.get("text", "") for p in parts).strip()
            if not answer:
                raise GeminiError("Gemini returned an empty response. Please try again.", True)
            return answer
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (429, 500, 502, 503, 504)
            if exc.code in (400, 401, 403):
                raise GeminiError("Gemini rejected the request or API key. Check backend configuration.", False) from exc
            raise GeminiError(f"Gemini service error ({exc.code}). Please try again.", retryable) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GeminiError("Network connection failed. ROSA can still use offline commands.", True) from exc
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise GeminiError("Gemini response could not be read. Please try again.", True) from exc
