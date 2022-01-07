import discord
import random
import datetime as dt
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord_slash import cog_ext
import discord_music_bot as main
from discord_slash.utils.manage_commands import create_option

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
music_queue = []


# searching the item on YouTube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            # print(info)
        except:
            return False

    return {'source': info['formats'][0]['url'], 'title': info['title'], 'thumbnail': info['thumbnail'],
            'duration': info['duration']}


class PlayC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # 2d array containing [song, channel]

    def announce_song(self, ctx, a):
        embed = discord.Embed(title="Currently playing:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        embed.set_thumbnail(url=a[0]['thumbnail'])
        embed.add_field(name=a[0]['title'],
                        value=str(dt.timedelta(seconds=int(a[0]['duration']))),
                        inline=True)
        self.bot.loop.create_task(ctx.send(embed=embed))

    def play_next(self, ctx, vc):
        if len(music_queue) > 0:
            # get the first url and
            # remove the selected element as you are currently playing it
            if not vc.is_playing():
                if main.bot.shuffle:
                    a = random.choice(music_queue)
                    m_url = a[0]['source']
                    self.announce_song(ctx, a)
                    music_queue.remove(a)
                else:
                    m_url = music_queue[0][0]['source']
                    self.announce_song(ctx, music_queue[0])
                    music_queue.pop(0)
                vc.play(discord.FFmpegPCMAudio(options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                               source=m_url), after=lambda e: self.play_next(ctx, vc))

    # infinite loop checking
    async def play_music(self, ctx, vc):
        if len(music_queue) > 0:
            m_url = music_queue[0][0]['source']
            # try to connect to voice channel if you are not already connected
            if vc == "" or vc is None:
                vc = await music_queue[0][1].connect()
            else:
                await vc.move_to(music_queue[0][1])
            # remove the first element as you are currently playing it
            if not vc.is_playing():
                if main.bot.announce:
                    self.announce_song(ctx, music_queue[0])
                music_queue.pop(0)
                vc.play(discord.FFmpegPCMAudio(options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                               source=m_url), after=lambda e: self.play_next(ctx, vc))

    @cog_ext.cog_slash(name="play",
                       description="Play a song",
                       options=[
                           create_option(
                               name="music",
                               description="the music to be played",
                               option_type=3,
                               required=True
                           )],
                       guild_ids=[663825004256952342])
    async def play(self, ctx, music: str):
        query = " ".join(music)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to "
                    "playlist or a livestream format.")
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
                await self.play_music(ctx, voice)

    @cog_ext.cog_slash(name="queue",
                       description="Displays the songs in the queue",
                       guild_ids=[663825004256952342])
    async def queue(self, ctx):
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


def setup(bot):
    bot.add_cog(PlayC(bot))
