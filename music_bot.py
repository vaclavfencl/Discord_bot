import discord
import asyncio
from discord.ext import commands
import yt_dlp
from discord import FFmpegPCMAudio

from bot_config import load_token


#---------------SETUP---------------#

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True
intents.voice_states = True
client = commands.Bot(command_prefix='!', intents=intents)


#---------------EVENTS---------------#

@client.event
async def on_ready():
    print("Bot is ready")
    print("--------------------------------------")


#---------------COMMANDS---------------#
@client.command(pass_context = True)
async def join(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in voice channel, you must be in a voice channel to run this command")

@client.command(pass_context = True)
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel")

@client.command()
async def play(ctx, *, arg: str):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel.")
        return

    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()

    if "youtube.com" in arg or "youtu.be" in arg:
        search_query = arg  # It's a direct URL
    else:
        search_query = f"ytsearch:{arg}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_audio': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)
        if "entries" in info:
            info = info["entries"][0]

        url2 = info["url"]
        title = info.get("title", "Unknown title")

    voice = ctx.voice_client
    source = FFmpegPCMAudio(url2)
    voice.play(source)

    await ctx.send(f"🎵 Now playing: **{title}**")
    await idle_disconnect(ctx)

async def idle_disconnect(ctx):
    await asyncio.sleep(300)  # 5 minutes

    voice = ctx.voice_client
    if voice and not voice.is_playing():
        await voice.disconnect()
        await ctx.send("🚶 Bot disconnected due to inactivity.")

@client.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("There's no audio playing")

@client.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("There's no audio paused")

@client.command(pass_context = True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
    else:
        await ctx.send("There's no audio playing")
        
#---------------RUN---------------#

if __name__ == "__main__":
    client.run(load_token())
