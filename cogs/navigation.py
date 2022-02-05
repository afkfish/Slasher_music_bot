import discord
from discord.ext import commands
from discord_slash import cog_ext

import discord_music_bot as main
from cogs.play import Play


class Navigation(commands.Cog):

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
                obj = Play(commands.Cog)
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
        await ctx.send("")

    @cog_ext.cog_subcommand(base="clear",
                            name="duplicates",
                            description="Clear duplicated songs from queue.",
                            guild_ids=main.bot.guild_ids)
    async def clear_dup(self, ctx):
        if main.bot.music_queue[ctx.guild.id]:
            for i in range(len(main.bot.music_queue[ctx.guild.id])):
                for j in range(len(main.bot.music_queue[ctx.guild.id])):
                    if main.bot.music_queue[ctx.guild.id][i][0]['title'] == main.bot.music_queue[ctx.guild.id][j][0]['title'] and i != j:
                        main.bot.music_queue[ctx.guild.id].remove(main.bot.music_queue[ctx.guild.id][i])
        embed = discord.Embed(title="Duplicated songs cleared! :broom:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        songs = Play.slist(ctx)
        if songs != "":
            embed.add_field(name="Songs: ", value=songs, inline=True)
        else:
            embed.add_field(name="Songs: ", value="No music in queue", inline=True)
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(base="clear",
                            name="all",
                            description="Clear all songs from queue.",
                            guild_ids=main.bot.guild_ids)
    async def clear_all(self, ctx):
        if main.bot.music_queue[ctx.guild.id]:
            main.bot.music_queue[ctx.guild.id] = []
        embed = discord.Embed(title="Queue cleared! :broom:", color=0x152875)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Navigation(bot))
