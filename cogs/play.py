import discord
import random
import json
import datetime as dt
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord_slash import cog_ext
import discord_music_bot as main
from discord_slash.utils.manage_commands import create_option

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
JSON_FORMAT = {'name': '', 'songs': []}


# searching the item on YouTube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            # print(info)
        except ValueError:
            return False

    return {'source': info['formats'][0]['url'], 'title': info['title'], 'thumbnail': info['thumbnail'],
            'duration': info['duration']}


class Play(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def slist(ctx):
        slist = ""
        for song in main.bot.music_queue[ctx.guild.id]:
            slist += song[0]['title'] + "\n"
        return slist

    def announce_song(self, ctx, a):
        embed = discord.Embed(title="Currently playing:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        embed.set_thumbnail(url=a[0]['thumbnail'])
        embed.add_field(name=a[0]['title'],
                        value=str(dt.timedelta(seconds=int(a[0]['duration']))),
                        inline=True)
        self.bot.loop.create_task(ctx.send(embed=embed))

    def play_next(self, ctx, vc):
        if len(main.bot.music_queue[ctx.guild.id]) > 0:
            # get the first url and
            # remove the selected element as you are currently playing it
            if not vc.is_playing():
                if main.bot_shuffle(ctx.guild.id):
                    a = random.choice(main.bot.music_queue[ctx.guild.id])
                    m_url = a[0]['source']
                    if main.bot_announce(ctx.guild.id):
                        self.announce_song(ctx, a)
                    main.bot.playing[ctx.guild.id] = a
                    main.bot.music_queue[ctx.guild.id].remove(a)
                else:
                    m_url = main.bot.music_queue[ctx.guild.id][0][0]['source']
                    if main.bot_announce(ctx.guild.id):
                        self.announce_song(ctx, main.bot.music_queue[ctx.guild.id][0])
                    main.bot.playing[ctx.guild.id] = main.bot.music_queue[ctx.guild.id][0]
                    main.bot.music_queue[ctx.guild.id].pop(0)
                if vc.is_connected:
                    vc.play(discord.FFmpegPCMAudio(options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                                                   source=m_url), after=lambda e: self.play_next(ctx, vc))

    # infinite loop checking
    async def play_music(self, ctx, vc):
        if len(main.bot.music_queue[ctx.guild.id]) > 0:
            m_url = main.bot.music_queue[ctx.guild.id][0][0]['source']
            # try to connect to voice channel if you are not already connected
            if vc == "" or vc is None:
                vc = await main.bot.music_queue[ctx.guild.id][0][1].connect()
            else:
                await vc.move_to(main.bot.music_queue[ctx.guild.id][0][1])
            # remove the first element as you are currently playing it
            if not vc.is_playing():
                if main.bot_announce(ctx.guild.id):
                    self.announce_song(ctx, main.bot.music_queue[ctx.guild.id][0])
                main.bot.playing[ctx.guild.id] = main.bot.music_queue[ctx.guild.id][0]
                main.bot.music_queue[ctx.guild.id].pop(0)
                if vc.is_connected:
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
                       guild_ids=main.bot.guild_ids)
    async def play(self, ctx, music):
        query = "".join(music)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = search_yt(query)
            if song is False:
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to "
                    "playlist or a livestream format.")
            else:
                main.bot.music_queue[ctx.guild.id].append([song, voice_channel])
                embed = discord.Embed(title="Song added to queue", color=0x152875)
                embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
                embed.set_thumbnail(url=main.bot.music_queue[ctx.guild.id][-1][0]['thumbnail'])
                embed.add_field(name=main.bot.music_queue[ctx.guild.id][-1][0]['title'],
                                value=str(dt.timedelta(
                                    seconds=int(main.bot.music_queue[ctx.guild.id][-1][0]['duration']))),
                                inline=True)
                embed.set_footer(text="Song requested by: " + ctx.author.name)
                await ctx.send(embed=embed)
                await self.play_music(ctx, voice)

    @cog_ext.cog_slash(name="queue",
                       description="Displays the songs in the queue",
                       guild_ids=main.bot.guild_ids)
    async def queue(self, ctx):
        embed = discord.Embed(title="Queue", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        songs = self.slist(ctx)
        if songs != "":
            embed.add_field(name="Songs: ", value=songs, inline=True)
        else:
            embed.add_field(name="Songs: ", value="No music in queue", inline=True)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="createpl",
                       description="Create playlists",
                       options=[
                           create_option(name="name",
                                         description=" ",
                                         option_type=3,
                                         required=True)
                       ],
                       guild_ids=main.bot.guild_ids)
    async def createplaylist(self, ctx, name):
        JSON_FORMAT['name'] = name
        with open("./playlists/{}.json".format(name), "w") as f:
            json.dump(JSON_FORMAT, f, indent=4)
        f.close()
        await ctx.send("Playlis {} was succefully created".format(name))

    @cog_ext.cog_slash(name="addsong",
                       description="Append a song to existing playlists",
                       options=[
                           create_option(name="playlist",
                                         description="the destination playlist",
                                         option_type=3,
                                         required=True),
                           create_option(name="song",
                                         description="the song's URL",
                                         option_type=3,
                                         required=True)
                       ],
                       guild_ids=main.bot.guild_ids)
    async def addsong(self, ctx, playlist, song):
        with open("./playlists/{}.json".format(playlist), "r") as a:
            data = json.load(a)
        data['songs'].append(song)
        with open("./playlists/{}.json".format(playlist), "w") as f:
            json.dump(data, f, indent=4)
        await ctx.send("Song was successfully added!")

    @cog_ext.cog_slash(name="playlist",
                       description="Play songs from a playlist",
                       options=[
                           create_option(name="playlist_name",
                                         description="the name of the playlist",
                                         option_type=3,
                                         required=True)
                       ],
                       guild_ids=main.bot.guild_ids)
    async def playlist(self, ctx, playlist_name):
        with open("./playlists/{}.json".format(playlist_name), "r") as f:
            data = json.load(f)
        for item in data['songs']:
            vc = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            voice_channel = ctx.author.voice.channel
            if voice_channel is None:
                await ctx.send("Connect to a voice channel!")
            else:
                song = search_yt(item)
                print(item)
                if song is False:
                    await ctx.send("Could not play the song from the playlist.")
                else:
                    main.bot.music_queue.append([song, voice_channel])
                    await self.play_music(ctx, vc)
        await ctx.send("Playlist succefully loaded!")

    @cog_ext.cog_slash(name="np",
                       description="The song that is currently being played",
                       guild_ids=main.bot.guild_ids)
    async def np(self, ctx):
        self.announce_song(ctx, main.bot.playing[ctx.guild.id])


def setup(bot):
    bot.add_cog(Play(bot))
