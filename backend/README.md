# ROSA AI Gateway

Deploy this service on a trusted HTTPS host. Set these environment variables in the host dashboard:

- `GEMINI_API_KEY`: the private Gemini key (never commit it or place it in the Android app).
- `ROSA_PROXY_TOKEN`: a long random bearer token for development only. For production mobile distribution, replace the shared token with per-user authentication (for example Firebase Auth) and server-side rate limits.

Run locally:

```bash
python -m pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
export ROSA_PROXY_TOKEN="generate-a-long-random-secret"
uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

The `/health` endpoint reveals only whether a key is configured. `/v1/chat` requires a bearer token. Do not expose the service without authentication, HTTPS, abuse controls and quotas.
