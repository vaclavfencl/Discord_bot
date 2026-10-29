# Discord Moderation and Activity Bot

A Python Discord bot for clearing channel messages and tracking server activity. The main script, `chat_bot.py`, includes permission-based message cleanup, message counts, voice-session time tracking, and an activity report updated every hour. Some activity-report text is in Czech.

`music_bot.py` is a separate, secondary script for experimenting with voice playback. It is not required for moderation or activity tracking.

## Main feature: clear messages

Use `!clear` to remove recent messages from the current text channel:

```text
!clear 10
```

This attempts to delete the 10 most recent messages plus the command message itself. The amount must be a positive whole number. Only members with **Manage Messages** permission can use the command. The bot needs **View Channel**, **Read Message History**, **Send Messages**, and **Manage Messages** in that channel.

Deletion is permanent. Channel permissions, deleted messages, and Discord API limits can affect the result; this is intended for recent-message cleanup rather than deleting an entire channel history.

## Setup

1. Install Python 3.11 or newer and make sure `python` is available on PATH.
2. On Windows, double-click `install_dependencies.bat`, or open a terminal in this folder and run:

   ```sh
   python -m pip install -r requirements.txt
   ```

3. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications). Under **Bot → Privileged Gateway Intents**, enable **Message Content Intent** and **Server Members Intent**, which are requested by these scripts. See the [discord.py intents guide](https://discordpy.readthedocs.io/en/stable/intents.html).
4. Invite the bot to your server with the permissions listed above. Members using `!setstatschannel` also need **Manage Channels**.
5. Copy `config.txt.example` to `config.txt` next to the scripts. Replace the placeholder with your bot token, without quotation marks:

   ```ini
   token = CHANGE_THIS_TEXT_FOR_YOUR_DISCORD_BOT_TOKEN
   ```

6. Start the main bot:

   ```sh
   python chat_bot.py
   ```

Both scripts read the same configuration. Existing `config.txt` files containing only the token are also supported. Keep the real token private; `.gitignore` excludes `config.txt` and the generated activity data.

## Main bot commands

| Command | Description | Member permission |
| --- | --- | --- |
| `!clear <amount>` | Delete recent messages plus the command message. | Manage Messages |
| `!setstatschannel` | Use the current channel for the hourly activity report. | Manage Channels |
| `!activity` | Show recorded message counts and voice-session times. | No additional permission |

Activity is stored per server in `stats.json` next to the script. The file is created automatically. Reports show cumulative totals; they refresh hourly but do not reset the counters. Voice time is added when a member leaves voice, so an ongoing session is not included yet. Tracking depends on the bot being online and observing the session events.

## Secondary script: music bot

The music bot accepts YouTube URLs or search terms and uses `yt-dlp` and FFmpeg to send audio to a Discord voice channel. Run it separately from the main bot. Use one script at a time with a shared token; to run both independently, use separate bot applications and separate copies of the folder with their own configuration.

Install its Python dependencies from this folder:

```bat
install_dependencies.bat music
```

Or use:

```sh
python -m pip install --upgrade -r requirements-music.txt
```

Voice support is installed through `discord.py[voice]`. You must separately install [FFmpeg](https://ffmpeg.org/download.html) and [Deno](https://deno.com/), and make their executables available on PATH. FFmpeg handles audio playback; current `yt-dlp` YouTube support also uses a JavaScript runtime. The music requirements include the `yt-dlp[default]` extras. See the [yt-dlp dependency documentation](https://github.com/yt-dlp/yt-dlp#dependencies).

Give the bot **View Channel**, **Send Messages**, **Connect**, and **Speak** permissions, then run:

```sh
python music_bot.py
```

| Command | Description |
| --- | --- |
| `!join` | Join your voice channel. |
| `!leave` | Disconnect from voice. |
| `!play <YouTube URL or search terms>` | Play a single audio stream. You must be in voice. |
| `!pause` | Pause playback. |
| `!resume` | Resume paused playback. |
| `!stop` | Stop playback. |

There is no music queue. After `!play`, the script checks once after five minutes and disconnects if no audio is playing. Playback depends on external services and may stop working when those services change. No local `sound.wav` file is needed.

### YouTube terms notice

Using this script to extract and relay YouTube audio without the required authorization violates [YouTube's Terms of Service](https://www.youtube.com/static?template=terms). Those terms restrict automated access and accessing or transmitting content outside the service's authorized features. This project does not grant permission from YouTube or any copyright holder. The music script is included as a secondary technical demonstration; users are responsible for obtaining the required permissions and complying with service terms and applicable law.

## Disclaimer

This software is provided **as is**, without warranties of any kind. Use it at your own risk. To the fullest extent permitted by applicable law, the author is not liable for any claims, damages, losses, account restrictions, deleted messages, or other liability arising from using or being unable to use this software. Users are responsible for their configuration, actions, and compliance with applicable laws and third-party terms.
