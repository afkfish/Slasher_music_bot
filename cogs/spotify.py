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
        embed = discord.Embed(title="Song added to queue from Spotify <:spotify:944554099175727124>",
                              color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        artists = ""
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
                                seconds=int(int(song['duration_ms'])/1000)))))
            query = "{}\n{}".format(song['album']['name'], artists)
        else:
            song = SpotifyApi().get_by_name(q=music, limit=1, type="track")
            for artist in song['tracks']['items'][0]['artists']:
                artists += "".join("{}, ".format(artist['name']))
            artists = artists[:-2]
            embed.set_thumbnail(url=song['tracks']['items'][0]['album']['images'][0]['url'])
            embed.add_field(name="{}\n\n".format(song['tracks']['items'][0]['name']),
                            value="{}\n{}".format(artists, str(dt.timedelta(
                                seconds=int(int(song['tracks']['items'][0]['duration_ms'])/1000)))))
            query = "{}  {}".format(song['tracks']['items'][0]['name'], artists)
        embed.set_footer(text="Song requested by: " + ctx.author.name)
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            track = search_yt(query)
            if track is False:
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to "
                    "playlist or a livestream format.")
            else:
                main.bot.music_queue[ctx.guild.id].append([track, voice_channel])
                await Play(commands.cog).play_music(ctx, voice)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Spotify(bot))
