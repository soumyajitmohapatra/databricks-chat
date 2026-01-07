import asyncio
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

try:
    from databricks.sdk import GenieAPI, WorkspaceClient, errors
except Exception:  # databricks-sdk not installed yet
    GenieAPI = None
    WorkspaceClient = None
    errors = None

logger = logging.getLogger(__name__)

from const import DATABRICKS_HOST, DATABRICKS_CLIENT_ID, DATABRICKS_CLIENT_SECRET


@dataclass
class GenieReply:
    conversation_id: Optional[str]
    message: Optional[str]
    query_description: Optional[str] = None
    query_result_metadata: Optional[Dict[str, Any]] = None
    attachments: Optional[Any] = None


class GenieService:
    """Minimal wrapper around Databricks Genie API suitable for server-side use.

    - Uses an OAuth token (per-user) if provided to constructor
    - Falls back to service-principal if `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` are set
    """

    def __init__(
        self,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """Initialize GenieService.

        Priority for auth is:
        1) Service-principal (explicit client_id/client_secret or env vars)
        2) Token (explicit token)
        If neither is available the service will remain uninitialized (stub mode).
        """
        # Prefer explicit args, otherwise fallback to server constants
        self.token = token
        self.client_id = client_id or DATABRICKS_CLIENT_ID
        self.client_secret = client_secret or DATABRICKS_CLIENT_SECRET
        self.auth_method = None
        self.genie_api = None

        if not GenieAPI or not WorkspaceClient:
            logger.info("GenieAPI not available; running in stub mode")
            return

        # 1) Service principal (preferred)
        if self.client_id and self.client_secret:
            try:
                wc = WorkspaceClient(
                    host=DATABRICKS_HOST,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
                self.genie_api = GenieAPI(wc.api_client)
                self.auth_method = "service_principal"
                return
            except Exception:
                logger.exception("Failed to initialize GenieAPI with service principal")
                self.genie_api = None

        # 2) Token (fallback)
        if self.token:
            try:
                wc = WorkspaceClient(host=DATABRICKS_HOST, token=self.token)
                self.genie_api = GenieAPI(wc.api_client)
                self.auth_method = "oauth"
                return
            except Exception:
                logger.exception("Failed to initialize GenieAPI with token")
                self.genie_api = None

        logger.info("GenieAPI not initialized; no credentials available")

    async def ask_genie(
        self,
        text: str,
        space_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> GenieReply:
        """Send message to Genie and return a simplified reply structure.

        This is intentionally lightweight so the frontend can work with a simple JSON response.
        """
        if not self.genie_api:
            # Fallback stub so frontend works without SDK or credentials
            return GenieReply(
                conversation_id=conversation_id or "stub", message=f"(stub) {text}"
            )

        try:
            loop = asyncio.get_running_loop()

            if conversation_id is None:
                initial = await loop.run_in_executor(
                    None, self.genie_api.start_conversation_and_wait, space_id, text
                )
                conversation_id = getattr(initial, "conversation_id", conversation_id)
            else:
                initial = await loop.run_in_executor(
                    None,
                    self.genie_api.create_message_and_wait,
                    space_id,
                    conversation_id,
                    text,
                )

            message_content = await loop.run_in_executor(
                None,
                self.genie_api.get_message,
                space_id,
                initial.conversation_id,
                initial.message_id,
            )

            # Build a simple response payload
            message_text = getattr(message_content, "content", None)
            reply = GenieReply(
                conversation_id=getattr(
                    message_content, "conversation_id", conversation_id
                ),
                message=message_text,
            )

            # Attach minimal attachments info if present
            attachments = getattr(message_content, "attachments", None)
            if attachments:
                reply.attachments = [
                    {
                        "attachment_id": getattr(a, "attachment_id", None),
                        "text": getattr(getattr(a, "text", None), "content", None),
                    }
                    for a in attachments
                ]

            return reply

        except Exception as e:
            # Handle token expiry / permission denied gracefully
            if errors and isinstance(e, errors.platform.PermissionDenied):
                logger.warning("PermissionDenied from Genie API; token may be expired")
                return GenieReply(
                    conversation_id=conversation_id, message="TOKEN_EXPIRED"
                )

            logger.exception("Error while calling Genie API")
            return GenieReply(
                conversation_id=conversation_id,
                message="An error occurred while processing your request.",
            )
