import discord
import discord_music_bot as main
import datetime as dt
from utils.spotify_api_request import SpotifyApi
from cogs.play import search_yt, Play
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


class Spotify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="spotify",
                       description="search on spotify",
                       options=[
                           create_option(name="music",
                                         description="choose music",
                                         option_type=3,
                                         required=True)
                       ],
                       guild_ids=main.bot.guild_ids)
    async def spotify(self, ctx, music):
        msg = await ctx.send('Bot is thinking!')
        embed = discord.Embed(title=f"Song added to queue from Spotify {self.bot.get_emoji(944554099175727124)}",
                              color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        artists = ""
        query = []
        if "open.spotify.com/track" in music:
            a = music.split('track/')
            a = a[1].split('?si')
            song = SpotifyApi().get_by_id(trackid=a[0])
            for artist in song['album']['artists']:
                artists += "".join("{}, ".format(artist['name']))
            artists = artists[:-2]
            embed.set_thumbnail(url=song['album']['images'][0]['url'])
            embed.add_field(name="{}\n\n".format(song['name']),
                            value="{}\n{}".format(artists, str(dt.timedelta(
                                seconds=int(int(song['duration_ms']) / 1000)))))
            query.append("{}\n{}".format(song['album']['name'], artists))
        elif "open.spotify.com/playlist" in music:
            a = music.split("playlist/")
            a = a[1].split("?si")
            playlist = SpotifyApi().get_playlist(playlist_id=a[0])
            for song in playlist['tracks']['items']:
                artists = ""
                for artist in song['track']['artists']:
                    artists += "".join("{}, ".format(artist['name']))
                artists = artists[:-2]
                query.append("{}\n{}".format(song['track']['name'], artists))
            embed.set_thumbnail(url=playlist['images'][0]['url'])
            embed.add_field(name="{}\n\n".format(playlist['name']),
                            value="{}\n".format(playlist['owner']['display_name']))
        else:
            song = SpotifyApi().get_by_name(q=music, limit=1, type_="track")
            for artist in song['tracks']['items'][0]['artists']:
                artists += "".join("{}, ".format(artist['name']))
            artists = artists[:-2]
            embed.set_thumbnail(url=song['tracks']['items'][0]['album']['images'][0]['url'])
            embed.add_field(name="{}\n\n".format(song['tracks']['items'][0]['name']),
                            value="{}\n{}".format(artists, str(dt.timedelta(
                                seconds=int(int(song['tracks']['items'][0]['duration_ms']) / 1000)))))
            query.append("{}  {}".format(song['tracks']['items'][0]['name'], artists))
        embed.set_footer(text="Song requested by: " + ctx.author.name)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if ctx.author.voice:
            voice_channel = ctx.author.voice.channel
            for entry in query:
                track = search_yt(entry)
                if track is False:
                    await msg.edit(content="Could not download the song. Incorrect format try another keyword. This "
                                           "could be due to playlist or a livestream format.")
                else:
                    main.bot.music_queue[ctx.guild.id].append([track, voice_channel])
            if main.bot.music_queue[ctx.guild.id][0]:
                await Play(commands.cog).play_music(ctx, voice)
            await msg.edit(embed=embed)
        else:
            await msg.edit(content="Connect to a voice channel!")


def setup(bot):
    bot.add_cog(Spotify(bot))
