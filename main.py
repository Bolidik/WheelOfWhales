from bot.utils.json_loader import load_accounts


async def main():
    accounts = load_accounts()
    if not accounts:
        logger.error("<red>No accounts loaded. Exiting...</red>")
        return

    for account in accounts:
        session_name = account.get("session_name")
        if session_name:
            logger.info(f"<green>Starting bot for session: {session_name}</green>")
            await process(session_name)  # Pass session_name to the process function
        else:
            logger.warning("<yellow>Session name missing in accounts.json. Skipping...</yellow>")
