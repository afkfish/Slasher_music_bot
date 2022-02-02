import discord
import cogs.play as play
import discord_music_bot as main
from discord.ext import commands
from discord_slash import cog_ext


class NavigationC(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="skip",
                       description="Skip the current song",
                       guild_ids=main.bot.guild_ids)
    async def skip(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice != "" and voice:
            voice.stop()
            embed = discord.Embed(title="Skipped :next_track:")
            await ctx.send(embed=embed)
            # try to play next in the queue if it exists
            if voice.is_playing():
                obj = play.PlayC(commands.Cog)
                await obj.play_music(ctx, voice)

    @cog_ext.cog_slash(name="pause",
                       description="Pause the song",
                       guild_ids=main.bot.guild_ids)
    async def pause_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            embed = discord.Embed(title="Paused :pause_button:")
            await ctx.send(embed=embed)
            voice.pause()

    @cog_ext.cog_slash(name="resume",
                       description="Resume playing",
                       guild_ids=main.bot.guild_ids)
    async def resume_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            embed = discord.Embed(title="Resumed")
            await ctx.send(embed=embed)
            voice.resume()

    @cog_ext.cog_slash(name="stop",
                       description="Stop playing",
                       guild_ids=main.bot.guild_ids)
    async def stop_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        embed = discord.Embed(title="Stopped :stop_button:")
        await ctx.send(embed=embed)
        voice.stop()

    @cog_ext.cog_slash(name="leave",
                       description="Leave voice chat",
                       guild_ids=main.bot.guild_ids)
    async def leave_(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_connected():
            await voice.disconnect()
            await ctx.send("Disconnected!")

    @cog_ext.cog_slash(name="clear",
                       description="clear",
                       guild_ids=main.bot.guild_ids)
    async def clear(self, ctx):
        print()

    @cog_ext.cog_subcommand(base="clear",
                            name="duplicates",
                            description="Clear duplicated songs from queue.",
                            guild_ids=main.bot.guild_ids)
    async def clear_dup(self, ctx):
        if main.bot.music_queue:
            for i in range(len(main.bot.music_queue)):
                for j in range(len(main.bot.music_queue)):
                    if main.bot.music_queue[i][0]['title'] == main.bot.music_queue[j][0]['title'] and i != j:
                        main.bot.music_queue.remove(main.bot.music_queue[i])
        await ctx.send("Duplicates cleared!")

    @cog_ext.cog_subcommand(base="clear",
                            name="all",
                            description="Clear all songs from queue.",
                            guild_ids=main.bot.guild_ids)
    async def clear_all(self, ctx):
        if main.bot.music_queue:
            main.bot.music_queue = []
        await ctx.send("Queue cleared!")


def setup(bot):
    bot.add_cog(NavigationC(bot))
