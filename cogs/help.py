import discord
from discord.ext import commands
from discord_slash import cog_ext
import discord_music_bot as main


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="help",
                       description="Get info on commands.",
                       guild_ids=main.bot.guild_ids)
    async def help(self, ctx):
        await ctx.send("Commands: ")

    @cog_ext.cog_subcommand(base="help",
                            subcommand_group="commands",
                            name="play",
                            description="play command",
                            base_description="text commands",
                            guild_ids=main.bot.guild_ids)
    async def help_play(self, ctx):
        embed = discord.Embed(title="Play :arrow_forward:", color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        embed.add_field(name="Usage:", value="The play command accepts words and youtube links as an argument. "
                                             "The user must be in a voice channel when executing the command! "
                                             "The bot cannot play livestreams and videos that are age restricted! "
                                             "The bot will search for a video named as the argument or the link and "
                                             "try to stream it into the voice channel where the user is present.")
        await ctx.send(embed=embed)

