import discord
import random
import json
import datetime as dt
import youtube_transcript_api
from utils.genius_api_request import GeniusApi
from utils.lyrics_scrape import get_lyrics
from youtube_dl import YoutubeDL
from discord.ext import commands
from discord_slash import cog_ext
import discord_music_bot as main
from youtube_transcript_api import YouTubeTranscriptApi
from discord_slash.utils.manage_commands import create_option

YDL_OPTIONS = {"format": "bestaudio", "noplaylist": True}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                  'options': '-vn'}
JSON_FORMAT = {'name': '', 'songs': []}


# searching the item on YouTube
def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            if item.startswith("https://www.youtube.com/watch?v="):
                info = ydl.extract_info(item, download=False)
            else:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        except ValueError:
            return False

    return {'source': info['formats'][0]['url'], 'title': info['title'], 'thumbnail': info['thumbnail'],
            'duration': info['duration'], 'id': info['id']}


class Play(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def slist(ctx):
        slist = ""
        for song in main.bot.music_queue[ctx.guild.id]:
            slist += song[0]['title'] + "\n"
        return slist

    @staticmethod
    def announce_song(ctx, a, msg=None):
        embed = discord.Embed(title="Currently playing:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        embed.set_thumbnail(url=a[0]['thumbnail'])
        embed.add_field(name=a[0]['title'],
                        value=str(dt.timedelta(seconds=int(a[0]['duration']))),
                        inline=True)
        if msg is None:
            main.bot.loop.create_task(ctx.send(embed=embed))
        else:
            main.bot.loop.create_task(msg.edit(embed=embed))

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
                    vc.play(discord.FFmpegPCMAudio(before_options='-reconnect 1 -reconnect_streamed 1 '
                                                                  '-reconnect_delay_max 5',
                                                   source=m_url), after=lambda e: self.play_next(ctx, vc))

    # infinite loop checking
    async def play_music(self, ctx, vc):
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
                vc.play(discord.FFmpegPCMAudio(before_options='-reconnect 1 -reconnect_streamed 1 '
                                                              '-reconnect_delay_max 5',
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
        msg = await ctx.send('Bot is thinking!')
        query = "".join(music)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if ctx.author.voice:
            voice_channel = ctx.author.voice.channel
            song = search_yt(query)
            if not song:
                await msg.edit(content=
                               "Could not download the song. Incorrect format try another keyword. This could be due "
                               "to playlist or a livestream format.")
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
                await msg.edit(embed=embed)
                await self.play_music(ctx, voice)
        else:
            await msg.edit(content="Connect to a voice channel!")

    @cog_ext.cog_slash(name="queue",
                       description="Displays the songs in the queue",
                       guild_ids=main.bot.guild_ids)
    async def queue(self, ctx):
        msg = await ctx.send('Bot is thinking!')
        embed = discord.Embed(title="Queue", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        songs = self.slist(ctx)
        if songs != "":
            embed.add_field(name="Songs: ", value=songs, inline=True)
        else:
            embed.add_field(name="Songs: ", value="No music in queue", inline=True)
        await msg.edit(embed=embed)

    @cog_ext.cog_slash(name="createpl",
                       description="Create playlists",
                       options=[
                           create_option(name="name",
                                         description="playlist name",
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
                # print(item)
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
        msg = await ctx.send('Bot is thinking!')
        self.announce_song(ctx, main.bot.playing[ctx.guild.id], msg)

    @cog_ext.cog_slash(name="subtitle",
                       description="get the video subtitle",
                       guild_ids=main.bot.guild_ids)
    async def subtitle(self, ctx):
        try:
            sub = YouTubeTranscriptApi.get_transcripts(video_ids=[main.bot.playing[ctx.guild.id][0]['id']],
                                                       languages=['en'])
            formatted = "```"
            for text in sub[0][main.bot.playing[ctx.guild.id][0]['id']]:
                formatted += text['text'] + "\n"
            formatted += "```"
            await ctx.send("Subtitle:")
            await ctx.send(formatted)
        except youtube_transcript_api._errors.TranscriptsDisabled as e:
            print("{}".format(type(e).__name__, e))
            await ctx.send("Couldn't find subtitles!")

    @cog_ext.cog_slash(name="lyrics",
                       description="test",
                       guild_ids=main.bot.guild_ids)
    async def lyrics(self, ctx):
        await ctx.send('Bot is thinking!', delete_after=1)
        embed = discord.Embed(title="Song Lyrics:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        try:
            song = GeniusApi().get_song(main.bot.playing[ctx.guild.id][0]['title'])
            lyrics = get_lyrics(song)
            if len(lyrics) > 1000:
                ly1 = lyrics[:len(lyrics) // 2]
                ly2 = lyrics[len(lyrics) // 2:]
                embed.add_field(name=song['title'], value=ly1)
                embed2 = discord.Embed(color=0x152875)
                embed2.add_field(name="", value=ly2)
                embed.set_thumbnail(url=main.bot.playing[ctx.guild.id][0]['thumbnail'])
                await ctx.send(embed=embed)
                await ctx.send(embed=embed2)
            else:
                embed.add_field(name=song['title'], value=lyrics)
                embed.set_thumbnail(url=main.bot.playing[ctx.guild.id][0]['thumbnail'])
                await ctx.send(embed=embed)
        except IndexError as ex:
            print(f"{type(ex).__name__} {ex}")
            await ctx.send(f"Error: {ex}")


def setup(bot):
    bot.add_cog(Play(bot))
