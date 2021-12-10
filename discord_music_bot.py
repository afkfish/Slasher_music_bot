import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix='>')

# remove the default help command so that we can write out own
bot.remove_command('help')

# all the music related stuff

# 2d array containing [song, channel]
music_queue = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
vc = ""

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
    voice_channel = ctx.message.author.voice.channel
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
            print(music_queue)
            await ctx.send("Song added to queue.")
            await play_music(voice)


@bot.command()
async def q(ctx):
    retval = ""
    for i in range(0, len(music_queue)):
        retval += music_queue[i][0]['title'] + "\n"

    print(retval)
    if retval != "":
        await ctx.send(retval)
    else:
        await ctx.send("No music in queue")


@bot.command()
async def s(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != "" and voice:
        voice.stop()
        # try to play next in the queue if it exists
        await play_music(voice)

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()

# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
