import os
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from genie import GenieService
from const import (
    DATABRICKS_HOST,
    DATABRICKS_CLIENT_ID,
    DATABRICKS_CLIENT_SECRET,
    WELCOME_MESSAGE,
    WAITING_MESSAGE,
    SWITCHING_MESSAGE,
    TOKEN_EXPIRED_MESSAGE,
)

app = FastAPI()

# Serve React static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve React index.html at root
@app.get("/")
def serve_react():
    return FileResponse("static/index.html")


def _mask_secret(s: str | None) -> str | None:
    """Return a masked representation of a secret (keep start/end, mask middle)."""
    if s is None:
        return None
    if len(s) <= 6:
        return "***"
    return f"{s[:3]}...{s[-3:]}"


def get_genie_env(route: str | None = None) -> dict:
    """Return minimal environment variables used by Genie calls (secrets masked).

    This intentionally returns only the envs that the Genie integration uses so
    responses are concise and focused for debugging.
    """

    client_secret = DATABRICKS_CLIENT_SECRET

    minimal = {
        "DATABRICKS_HOST": DATABRICKS_HOST,
        "DATABRICKS_CLIENT_ID": DATABRICKS_CLIENT_ID,
        "DATABRICKS_CLIENT_SECRET": _mask_secret(client_secret),
    }

    # Both `message` and `verify` rely on the same minimal auth-related envs.
    return minimal


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for local/dev use; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenieRequest(BaseModel):
    text: str
    spaceId: Optional[str] = None
    conversationId: Optional[str] = None
    token: Optional[str] = None


@app.post("/api/genie/message")
async def genie_message(req: GenieRequest):
    """
    Endpoint that proxies a request to Databricks Genie via `server.genie.GenieService`.

    Uses per-user `token` if provided; otherwise falls back to service-principal credentials
    read from environment (`DATABRICKS_CLIENT_ID` / `DATABRICKS_CLIENT_SECRET`).
    """
    logger.info(
        f"/api/genie/message received: text={req.text!r}, spaceId={req.spaceId}, conversationId={req.conversationId}"
    )

    try:
        # Prefer explicitly-configured client secret from server constants; fallback to request token

        token = DATABRICKS_CLIENT_SECRET or req.token
        svc = GenieService(token=token)
        result = await svc.ask_genie(req.text, req.spaceId, req.conversationId)

        return {
            "conversationId": result.conversation_id,
            "message": result.message,
            "statusMessage": WAITING_MESSAGE,
            "switchingMessage": SWITCHING_MESSAGE,
            "queryDescription": result.query_description,
            "queryResultMetadata": result.query_result_metadata,
            "attachments": result.attachments,
            "env": get_genie_env("message"),
        }

    except Exception as e:
        logger.exception("Error handling /api/genie/message")
        raise HTTPException(status_code=500, detail=str(e))


class VerifyRequest(BaseModel):
    """Request body for /api/genie/verify.

    Clients should not send a token — verification uses the server-side
    environment (DATABRICKS_CLIENT_SECRET or service-principal credentials).
    """

    testText: Optional[str] = "hello"


@app.post("/api/genie/verify")
async def genie_verify(req: VerifyRequest):
    """Verify Databricks/Genie credentials.

    - If `token` is provided in the request body it will be used (user PAT / OAuth token).
    - Otherwise the server will use service-principal env vars (`DATABRICKS_CLIENT_ID`/`DATABRICKS_CLIENT_SECRET`).
    """
    logger.info("/api/genie/verify called")
    # Use explicit client credentials (if present) from server constants to construct GenieService.

    svc = GenieService(
        token=None,
        client_id=DATABRICKS_CLIENT_ID,
        client_secret=DATABRICKS_CLIENT_SECRET,
    )

    # Informative response when SDK/credentials not initialized
    if svc.genie_api is None:
        return {
            "ok": False,
            "auth_method": svc.auth_method,
            "message": "Genie SDK not initialized or credentials missing. Set service principal env vars or pass a token in the request body.",
            "env": get_genie_env("verify"),
        }

    try:
        # Do a lightweight test request
        result = await svc.ask_genie(req.testText or "hello", None, None)

        if result.message == "TOKEN_EXPIRED":

            return {
                "ok": False,
                "auth_method": svc.auth_method,
                "message": TOKEN_EXPIRED_MESSAGE,
                "env": get_genie_env("verify"),
            }

        return {
            "ok": True,
            "auth_method": svc.auth_method,
            "welcome_message": WELCOME_MESSAGE,
            "response_message": result.message,
            "conversationId": result.conversation_id,
            "env": get_genie_env("verify"),
        }

    except Exception:
        logger.exception("Error running verification against Genie")
        raise HTTPException(
            status_code=500, detail="Verification failed due to server error"
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
