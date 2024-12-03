import json
import os
from bot.utils import logger

SESSIONS_DIR = "sessions"
ACCOUNTS_FILE = "accounts.json"


def load_accounts():
    """Load accounts.json from the sessions directory."""
    accounts_path = os.path.join(SESSIONS_DIR, ACCOUNTS_FILE)
    try:
        with open(accounts_path, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
            logger.info(f"<green>Loaded accounts file: {accounts_path}</green>")
            return accounts
    except FileNotFoundError:
        logger.error(f"<red>Accounts file not found: {accounts_path}</red>")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"<red>Failed to parse accounts file: {e}</red>")
        return []


def get_account_by_session(session_name):
    """Retrieve account details by session name."""
    accounts = load_accounts()
    for account in accounts:
        if account.get("session_name") == session_name:
            return account
    logger.warning(f"<yellow>No account found for session: {session_name}</yellow>")
    return None
