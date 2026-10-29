from pathlib import Path


def load_token():
    """Read the Discord token from config.txt next to the scripts."""
    config_path = Path(__file__).with_name("config.txt")
    try:
        text = config_path.read_text(encoding="utf-8-sig").strip()
    except FileNotFoundError:
        raise RuntimeError(
            "Missing config.txt. Copy config.txt.example to config.txt "
            "and replace the placeholder with your Discord bot token."
        ) from None

    if "=" in text:
        key, _, value = text.partition("=")
        if key.strip().lower() != "token":
            raise ValueError("Use token = YOUR_DISCORD_BOT_TOKEN in config.txt.")
        token = value.strip()
    else:
        # Keep existing config files containing only the token working.
        token = text

    if not token or token == "CHANGE_THIS_TEXT_FOR_YOUR_DISCORD_BOT_TOKEN" or "\n" in token:
        raise ValueError("Set a single Discord bot token in config.txt.")

    return token
