# Server (FastAPI) for Chat App

This folder contains a small FastAPI server that serves the built React app and provides a placeholder `/api/genie/message` endpoint you can replace with real Genie integration.

Quick steps (local development):

1. Build the frontend and copy the static output into `server/static`:

   ```bash
   npm run build
   rm -rf server/static && cp -R dist server/static
   ```

2. Create a Python virtualenv and install server deps:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r server/requirements.txt
   ```

3. Add environment variables (use `server/.env.example` as a guide):

   ```bash
   cp server/.env.example server/.env
   # edit server/.env to add DATABRICKS_* values
   ```

4. Run the server (development):

   ```bash
   python server/app.py
   # or: uvicorn server.app:app --host 0.0.0.0 --port 8080 --reload
   ```

Verification endpoint

- You can verify credentials or a per-user token using the `/api/genie/verify` endpoint.

  Example (using a PAT / token directly):

  ```bash
  curl -s -H "Content-Type: application/json" \
    -d '{"token":"<your-pat>","testText":"hello"}' \
    http://localhost:8080/api/genie/verify | jq
  ```

  Example (using service principal env vars configured in `server/.env`):

  ```bash
  curl -s -H "Content-Type: application/json" -d '{}' http://localhost:8080/api/genie/verify | jq
  ```

Notes

- The server now includes `server/genie.py` which implements a lightweight `GenieService` wrapper. By default the service uses service-principal authentication (set `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` in `server/.env`), or you can pass a per-user `token` in the POST body to use user OAuth.
- The endpoint `/api/genie/message` expects JSON `{ text, spaceId?, conversationId?, token? }` and returns `{ conversationId, message, queryDescription, queryResultMetadata, attachments }`.
- For Databricks deployment make sure `server/static` contains the built frontend and required environment variables are set in Databricks job settings.
