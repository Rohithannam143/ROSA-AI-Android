# ROSA 3.0 — Python-first rebuild

This branch starts a clean rebuild. The previous app implementation is not used as the new foundation.

## Architecture
- Python package `rosa_core/`: intent parsing, conversation orchestration, safety policy and AI-provider adapters.
- Android shell (new implementation): Jetpack Compose UI, microphone/audio lifecycle, notifications, alarms, app intents and OS permission flows.
- Bridge contract: Python emits typed action proposals; Android validates them and asks for confirmation before consequential actions.
- Online AI: provider adapter through a secure backend proxy; no production API key embedded in the APK.
- Offline mode: deterministic local commands and graceful fallback when internet/AI is unavailable.

## Quality gates
Run Python tests:
```bash
python -m unittest discover -s tests -v
```

## Current status
This is the first clean Python core scaffold, not a finished Android application. The UI, Android bridge, voice pipeline, backend proxy, release signing and physical-device validation are still to be implemented.
