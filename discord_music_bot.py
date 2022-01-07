import discord
import random
import datetime as dt
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord.ext import commands
from youtube_dl import YoutubeDL

bot = commands.Bot(command_prefix='>')
slash = SlashCommand(bot, sync_commands=True)

# remove the default help command so that we can write out own
bot.remove_command('help')

# 2d array containing [song, channel]
music_queue = []
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
vc = ""
bot.shuffle = False
bot.announce = True


async def settings_embed(ctx):
    embed = discord.Embed(title="Settings",
                          description="The setting related to the bot",
                          color=0x152875)
    embed.set_author(name="Slasher",
                     icon_url="https://i.imgur.com/shZLAQk.jpg")
    embed.add_field(name="Prefix",
                    value="Currently the prefix is not changable due to lack of "
                          "knowledge the developer has",
                    inline=False)
    embed.add_field(name="Shuffle play :twisted_rightwards_arrows:",
                    value="Plays the songs shuffled\n\nEnabled: {}".format(
                        "True :white_check_mark:" if bot.shuffle else "False :x:"
                    ),
                    inline=True)
    embed.add_field(name="Announce songs :mega:",
                    value="Songs will be announced when played\n\nEnabled: {}".format(
                        "True :white_check_mark:" if bot.announce else "False :x:"
                    ),
                    inline=True)
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
            vc.play(discord.FFmpegPCMAudio(options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                           source=m_url), after=lambda e: play_next(ctx, vc))


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
            vc.play(discord.FFmpegPCMAudio(options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                           source=m_url), after=lambda e: play_next(ctx, vc))


@slash.slash(name="play", options=[
    create_option(
        name="music",
        description="the music to be played",
        option_type=3,
        required=True
    )], guild_ids=[663825004256952342])
async def play(ctx, music: str):
    query = " ".join(music)
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
            embed = discord.Embed(title="Song added to queue", color=0x152875)
            embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
            embed.set_thumbnail(url=music_queue[-1][0]['thumbnail'])
            embed.add_field(name=music_queue[-1][0]['title'],
                            value=str(dt.timedelta(seconds=int(music_queue[-1][0]['duration']))),
                            inline=True)
            embed.set_footer(text="Song requested by: " + ctx.author.name)
            await ctx.send(embed=embed)
            await play_music(ctx, voice)


@slash.slash(name="queue", guild_ids=[663825004256952342])
async def queue(ctx):
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


@slash.slash(name="skip", guild_ids=[663825004256952342])
async def skip(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != "" and voice:
        voice.stop()
        embed = discord.Embed(title="Skipped :next_track:")
        await ctx.send(embed=embed)
        # try to play next in the queue if it exists
        await play_music(ctx, voice)


@slash.slash(name="pause", guild_ids=[663825004256952342])
async def pause_(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        embed = discord.Embed(title="Paused :pause_button:")
        await ctx.send(embed=embed)
        voice.pause()


@slash.slash(name="resume", guild_ids=[663825004256952342])
async def resume_(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        embed = discord.Embed(title="Resumed")
        await ctx.send(embed=embed)
        voice.resume()


@slash.slash(name="stop", guild_ids=[663825004256952342])
async def stop_(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    embed = discord.Embed(title="Stopped :stop_button:")
    await ctx.send(embed=embed)
    voice.stop()


@slash.slash(name="leave", guild_ids=[663825004256952342])
async def leave_(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()


@slash.slash(name="settings", guild_ids=[663825004256952342])
async def settings_(ctx):
    await settings_embed(ctx)


@slash.subcommand(base="settings", name="play", subcommand_group="shuffle", options=[
    create_option(
        name="shuffle_play",
        description=" ",
        option_type=5,
        required=True,
    )
], guild_ids=[663825004256952342])
async def settings_shuffle(ctx, **shuffle_play: str):
    if bool(shuffle_play["shuffle_play"]):
        bot.shuffle = True
    elif not bool(shuffle_play["shuffle_play"]):
        bot.shuffle = False
    await settings_embed(ctx)


@slash.subcommand(base="settings", name="songs", subcommand_group="announce", options=[
    create_option(
        name="announce_songs",
        description=" ",
        option_type=5,
        required=True,
    )
], guild_ids=[663825004256952342])
async def settings_announce(ctx, **announce_songs: str):
    if bool(announce_songs['announce_songs']):
        bot.announce = True
    elif not bool(announce_songs['announce_songs']):
        bot.announce = False
    await settings_embed(ctx)


# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
