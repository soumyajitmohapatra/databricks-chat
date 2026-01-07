"""
Minimal replica of ChatX `const.py` for this project.
Loads environment variables and the `spaces.json` mapping.
"""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Log
logger = logging.getLogger(__name__)

# Env vars
load_dotenv()

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID")
DATABRICKS_CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET")
APP_ID = os.getenv("APP_ID", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
OAUTH_CONNECTION_NAME = os.getenv("OAUTH_CONNECTION_NAME", "")
WELCOME_MESSAGE = "Welcome to the Data Query Bot!"
WAITING_MESSAGE = "Querying Genie for results..."
SWITCHING_MESSAGE = "switch to @"
AUTH_METHOD = os.getenv("AUTH_METHOD", "oauth")  # can be 'oauth' or 'service_principal'


TOKEN_EXPIRED_MESSAGE = (
    "Oops, your token seems to have expired, please complete login process again."
)
