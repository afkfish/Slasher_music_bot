import discord
from discord import embeds
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.ext import commands
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix='>')
slash = SlashCommand(bot, sync_commands=True)

# remove the default help command so that we can write out own
bot.remove_command('help')

# 2d array containing [song, channel]
music_queue = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
vc = ""

# discord.opus.load_opus()


# searching the item on youtube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except Exception:
            return False

    return {'source': info['formats'][0]['url'], 'title': info['title']}


def play_next(vc):
    if len(music_queue) > 0:

        # get the first url
        m_url = music_queue[0][0]['source']

        # remove the first element as you are currently playing it
        if not vc.is_playing():
            music_queue.pop(0)
            vc.play(discord.FFmpegPCMAudio(m_url), after=lambda e: play_next(vc))


# infinite loop checking
async def play_music(vc):
    if len(music_queue) > 0:
        m_url = music_queue[0][0]['source']

        # try to connect to voice channel if you are not already connected
        if vc == "" or vc == None:
            vc = await music_queue[0][1].connect()
        else:
            await vc.move_to(music_queue[0][1])

        # remove the first element as you are currently playing it
        if not vc.is_playing():
            music_queue.pop(0)
            vc.play(discord.FFmpegPCMAudio(m_url), after=lambda e: play_next(vc))


@bot.command()
async def p(ctx, *args):
    query = " ".join(args)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        # you need to be connected so that the bot knows where to go
        await ctx.send("Connect to a voice channel!")
    else:
        song = search_yt(query)
        if type(song) == type(True):
            await ctx.send(
                "Could not download the song. Incorrect format try another keyword. This could be due to playlist or "
                "a livestream format.")
        else:
            music_queue.append([song, voice_channel])
            # print(music_queue)
            # await ctx.send("Song added to queue.")
            embed = discord.Embed(title="Song added to queue", color=0x152875)
            embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
            embed.add_field(name="{}".format(music_queue[-1][0]['title']), value="alma", inline=True)
            # embed.set_thumbnail(url="https://imgur.com/HDq0vCg")
            await ctx.send(embed=embed)
            await play_music(voice)


@slash.slash(name="play", options=[create_option(name="music", description="the music to be played", option_type=3, required=True)])
async def play(ctx: SlashContext, music: str):
    await p(ctx, music)


@bot.command()
async def q(ctx):
    retval = ""
    for i in range(0, len(music_queue)):
        retval += music_queue[i][0]['title'] + "\n"
    # print(retval)
    if retval != "":
        await ctx.send(retval)
    else:
        await ctx.send("No music in queue")


@slash.slash(name="queue")
async def queue(ctx):
    await q(ctx)


@bot.command()
async def s(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != "" and voice:
        voice.stop()
        # try to play next in the queue if it exists
        await play_music(voice)


@slash.slash(name="skip")
async def skip(ctx):
    await s(ctx)


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()


@slash.slash(name="pause")
async def pause_(ctx):
    await pause(ctx)


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()


@slash.slash(name="resume")
async def resume_(ctx):
    await resume(ctx)


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()


@slash.slash(name="stop")
async def stop_(ctx):
    await stop(ctx)


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()


@slash.slash(name="leave")
async def leave_(ctx):
    await leave(ctx)

# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
