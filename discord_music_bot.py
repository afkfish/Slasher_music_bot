import discord
import random
import datetime as dt
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
bot.shuffle = False
bot.announce = False

# discord.opus.load_opus()


async def settings_embed(ctx):
    embed = discord.Embed(title="Settings", description="The setting related to the bot", color=0x152875)
    embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
    embed.add_field(name="Prefix", value="Currently the prefix is not changable due to lack of "
                                         "knowledge the developer has", inline=False)
    embed.add_field(name="Shuffle play", value="Plays the songs shuffled\n"
                                               "\nEnabled: {}".format(bot.shuffle), inline=True)
    embed.add_field(name="Announce songs", value="Songs will be announced when played\n"
                                                 "\nEnabled: {}".format(bot.announce), inline=True)
    await ctx.send(embed=embed)


def announce_song(ctx, a):
    embed = discord.Embed(title="Currently playing:", color=0x152875)
    embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
    embed.set_thumbnail(url=a[0]['thumbnail'])
    embed.add_field(name=a[0]['title'],
                    value=str(dt.timedelta(seconds=int(a[0]['duration']))),
                    inline=True)
    bot.loop.create_task(ctx.send(embed=embed))


# searching the item on YouTube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            # print(info)
        except Exception:
            return False

    return {'source': info['formats'][0]['url'], 'title': info['title'], 'thumbnail': info['thumbnail'],
            'duration': info['duration']}


def play_next(ctx, vc):
    if len(music_queue) > 0:
        # get the first url and
        # remove the selected element as you are currently playing it
        if not vc.is_playing():
            if bot.shuffle:
                a = random.choice(music_queue)
                m_url = a[0]['source']
                announce_song(ctx, a)
                music_queue.remove(a)
            else:
                m_url = music_queue[0][0]['source']
                announce_song(ctx, music_queue[0])
                music_queue.pop(0)
            vc.play(discord.FFmpegPCMAudio(m_url), after=lambda e: play_next(ctx, vc))


# infinite loop checking
async def play_music(ctx, vc):
    if len(music_queue) > 0:
        m_url = music_queue[0][0]['source']

        # try to connect to voice channel if you are not already connected
        if vc == "" or vc == None:
            vc = await music_queue[0][1].connect()
        else:
            await vc.move_to(music_queue[0][1])

        # remove the first element as you are currently playing it
        if not vc.is_playing():
            if bot.announce:
                announce_song(ctx, music_queue[0])
            music_queue.pop(0)
            vc.play(discord.FFmpegPCMAudio(m_url), after=lambda e: play_next(ctx, vc))


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
            # print(music_queue[-1])
            # await ctx.send("Song added to queue.")
            embed = discord.Embed(title="Song added to queue", color=0x152875)
            embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
            embed.set_thumbnail(url=music_queue[-1][0]['thumbnail'])
            embed.add_field(name=music_queue[-1][0]['title'],
                            value=str(dt.timedelta(seconds=int(music_queue[-1][0]['duration']))),
                            inline=True)
            embed.set_footer(text="Song requested by: "+ctx.author.name)
            await ctx.send(embed=embed)
            await play_music(ctx, voice)


@slash.slash(name="play", options=[create_option(name="music", description="the music to be played", option_type=3,
                                                 required=True)])
async def play(ctx: SlashContext, music: str):
    await p(ctx, music)


@bot.command()
async def q(ctx):
    retval = ""
    embed = discord.Embed(title="Queue", color=0x152875)
    embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
    for i in range(0, len(music_queue)):
        retval += music_queue[i][0]['title'] + "\n"
    # print(retval)
    if retval != "":
        embed.add_field(name="Songs: ", value=retval, inline=True)
        await ctx.send(embed=embed)
    else:
        embed.add_field(name="Songs: ", value="No music in queue", inline=True)
        await ctx.send(embed=embed)


@slash.slash(name="queue")
async def queue(ctx):
    await q(ctx)


@bot.command()
async def s(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != "" and voice:
        voice.stop()
        embed = discord.Embed(title="Skipped")
        await ctx.send(embed=embed)
        # try to play next in the queue if it exists
        await play_music(ctx, voice)


@slash.slash(name="skip")
async def skip(ctx):
    await s(ctx)


@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        embed = discord.Embed(title="Paused")
        await ctx.send(embed=embed)
        voice.pause()


@slash.slash(name="pause")
async def pause_(ctx):
    await pause(ctx)


@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        embed = discord.Embed(title="Resumed")
        await ctx.send(embed=embed)
        voice.resume()


@slash.slash(name="resume")
async def resume_(ctx):
    await resume(ctx)


@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    embed = discord.Embed(title="Stopped")
    await ctx.send(embed=embed)
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


@bot.command()
async def settings(ctx, *arg):
    if len(arg) == 0:
        await settings_embed(ctx)
    else:
        match (arg[1]):
            case "true":
                match (arg[0]):
                    case "shuffle":
                        bot.shuffle = True
                    case "announce":
                        bot.announce = True
                await settings_embed(ctx)
            case "false":
                match (arg[0]):
                    case "shuffle":
                        bot.shuffle = False
                    case "announce":
                        bot.announce = False
                await settings_embed(ctx)
            case _:
                await settings_embed(ctx)
# TODO: slash command for settings
# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
