import discord
import cogs.play as play
from discord.ext import commands
from discord_slash import cog_ext


class NavigationC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="skip",
                       description="Skip the current song",
                       guild_ids=[663825004256952342])
    async def skip(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice != "" and voice:
            voice.stop()
            embed = discord.Embed(title="Skipped :next_track:")
            await ctx.send(embed=embed)
            # try to play next in the queue if it exists
            obj = play.PlayC(commands.Cog)
            await obj.play_music(ctx, voice)

    @cog_ext.cog_slash(name="pause",
                       description="Pause the song",
                       guild_ids=[663825004256952342])
    async def pause_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            embed = discord.Embed(title="Paused :pause_button:")
            await ctx.send(embed=embed)
            voice.pause()

    @cog_ext.cog_slash(name="resume",
                       description="Resume playing",
                       guild_ids=[663825004256952342])
    async def resume_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            embed = discord.Embed(title="Resumed")
            await ctx.send(embed=embed)
            voice.resume()

    @cog_ext.cog_slash(name="stop",
                       description="Stop playing",
                       guild_ids=[663825004256952342])
    async def stop_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        embed = discord.Embed(title="Stopped :stop_button:")
        await ctx.send(embed=embed)
        voice.stop()

    @cog_ext.cog_slash(name="leave",
                       description="Leave voice chat",
                       guild_ids=[663825004256952342])
    async def leave_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()


def setup(bot):
    bot.add_cog(NavigationC(bot))
