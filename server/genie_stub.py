"""
Minimal stub / shim for integrating Databricks Genie.

Replace or extend this with the `GenieQuerier` logic from the ChatX project when you're ready.
"""

import os
from dataclasses import dataclass

try:
    from databricks.sdk import GenieAPI, WorkspaceClient
except Exception:  # databricks-sdk may not be installed yet
    GenieAPI = None
    WorkspaceClient = None


@dataclass
class GenieResponse:
    conversation_id: str
    message: str
    query_description: str | None = None
    query_result_metadata: dict | None = None
    attachments: object | None = None


class GenieService:
    def __init__(self, token: str | None = None):
        from const import (
            DATABRICKS_HOST,
            DATABRICKS_CLIENT_ID,
            DATABRICKS_CLIENT_SECRET,
        )

        self.token = token
        self.host = DATABRICKS_HOST

        if GenieAPI and WorkspaceClient and token:
            wc = WorkspaceClient(host=self.host, token=token)
            self.genie_api = GenieAPI(wc.api_client)
            self.auth_method = "oauth"
        elif (
            GenieAPI
            and WorkspaceClient
            and DATABRICKS_CLIENT_ID
            and DATABRICKS_CLIENT_SECRET
        ):
            wc = WorkspaceClient(
                host=self.host,
                client_id=DATABRICKS_CLIENT_ID,
                client_secret=DATABRICKS_CLIENT_SECRET,
            )
            self.genie_api = GenieAPI(wc.api_client)
            self.auth_method = "service_principal"
        else:
            self.genie_api = None
            self.auth_method = None

    async def ask_genie(
        self, text: str, space_id: str | None = None, conversation_id: str | None = None
    ) -> GenieResponse:
        if self.genie_api is None:
            # Fallback stub
            return GenieResponse(
                conversation_id=conversation_id or "stub", message=f"(stub) {text}"
            )

        # TODO: Implement real calls using self.genie_api (or import GenieQuerier from ChatX)
        return GenieResponse(
            conversation_id=conversation_id or "real-not-implemented",
            message="(not implemented)",
        )
