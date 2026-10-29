import discord
import json
from discord.ext import commands, tasks
from datetime import datetime, timezone
from pathlib import Path

from bot_config import load_token

#---------------FILES---------------#

STATS_PATH = Path(__file__).with_name("stats.json")
    
#---------------SETUP---------------#

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True
intents.messages = True
intents.guilds = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)


def load_stats():
    try:
        with STATS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_stats():
    with STATS_PATH.open("w", encoding="utf-8") as f:
        json.dump(server_data, f, indent=4)


server_data = load_stats()

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"strávil {int(hours):02} hodin, {int(minutes):02} minut a {int(seconds):02} sekund online"

#---------------EVENTS---------------#

@client.event
async def on_ready():
    print(f"{client.user} is online and tracking activity!")
    if not reset_activity.is_running():
        reset_activity.start()

@client.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    if guild_id not in server_data:
        server_data[guild_id] = {"stats_room": None, "messages": {}, "voice": {}}

    server_data[guild_id]["messages"][user_id] = (
        server_data[guild_id]["messages"].get(user_id, 0) + 1
    )

    save_stats()
    await client.process_commands(message)

@client.event
async def on_voice_state_update(member, before, after):
    guild_id = str(member.guild.id)
    user_id = str(member.id)

    if guild_id not in server_data:
        server_data[guild_id] = {"stats_room": None, "messages": {}, "voice": {}}

    if before.channel is None and after.channel is not None:
        server_data[guild_id].setdefault("voice_join_time", {})[user_id] = datetime.now(timezone.utc).timestamp()

    elif before.channel is not None and after.channel is None:
        if user_id in server_data[guild_id].get("voice_join_time", {}):
            join_time = server_data[guild_id]["voice_join_time"].pop(user_id)
            time_spent = datetime.now(timezone.utc).timestamp() - join_time
            server_data[guild_id]["voice"][user_id] = (
                server_data[guild_id]["voice"].get(user_id, 0) + int(time_spent)
            )
            save_stats()

#---------------TASKS---------------#

@tasks.loop(hours=1)
async def reset_activity():
    for guild_id, data in server_data.items():
        stats_channel_id = data.get("stats_room")
        if not stats_channel_id:
            continue  

        guild = client.get_guild(int(guild_id))
        if not guild:
            continue

        channel = guild.get_channel(int(stats_channel_id))
        if not channel:
            continue

        last_message = None
        async for message in channel.history(limit=10):
            if message.author == client.user:
                last_message = message
                break

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        updated_text = f"**Hourly Activity Report** (Last Updated: {now})\n\n Počet poslaných zpráv: \n"
        
        if data["messages"]:
            updated_text += "\n".join([f"<@{user_id}> napsal {count} zpráv" for user_id, count in data["messages"].items()])
        
        updated_text += "\n\n Čas strávený pomlouváním ostatních:\n"
        if data["voice"]:
            updated_text += "\n".join([f"<@{user_id}> {format_time(time)}" for user_id, time in data["voice"].items()])

        try:
            if last_message:
                await last_message.edit(content=updated_text)  
            else:
                await channel.send(updated_text) 
        except discord.Forbidden:
            print(f"Missing permissions to edit messages in {guild.name}")

    save_stats()

#---------------COMMANDS---------------#
@client.command()
async def clear(ctx, amount: str = None):
    
    if not ctx.author.guild_permissions.manage_messages:
        return
    try:
        count = int(amount)
        if count <= 0:
            raise ValueError
    except (TypeError, ValueError):
        await ctx.send("Invalid amount. Use !clear X with a positive whole number.")
        return

    await ctx.channel.purge(limit=count + 1)

@client.command()
@commands.has_permissions(manage_channels=True)
async def setstatschannel(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id not in server_data:
        server_data[guild_id] = {"stats_room": None, "messages": {}, "voice": {}}

    server_data[guild_id]["stats_room"] = ctx.channel.id
    save_stats()

@client.command()
async def activity(ctx):
    guild_id = str(ctx.guild.id)
    messages = server_data.get(guild_id, {}).get("messages", {})
    voice_times = server_data.get(guild_id, {}).get("voice", {})

    if messages:
        leaderboard = "\n".join([f"<@{user_id}>: {count} messages" for user_id, count in messages.items()])
        await ctx.send(f"**Current Activity:**\n{leaderboard}")

    if voice_times:
        leaderboard = "\n".join([f"<@{user_id}> {format_time(time)}" for user_id, time in voice_times.items()])
        await ctx.send(f"**Current Voice Activity:**\n{leaderboard}")

#---------------RUN---------------#

if __name__ == "__main__":
    client.run(load_token())
