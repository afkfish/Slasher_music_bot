import discord
from discord.ext import commands
from discord_slash import cog_ext
import discord_music_bot as main


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def help_embed(ctx, command: str):
        embed = discord.Embed(color=0x152875)
        embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
        match command:
            case "play":
                embed.title = "Play :arrow_forward:"
                embed.add_field(name="Usage:", value="The play command accepts words and youtube links as an argument. "
                                                     "The user must be in a voice channel when executing the command! "
                                                     "The bot cannot play livestreams and videos that are age "
                                                     "restricted! "
                                                     "The bot will search for a video named as the argument or the "
                                                     "link and "
                                                     "try to stream it into the voice channel where the user is "
                                                     "present.")
            case "spotify":
                embed.title = "Spotify <:spotify:940575531567546369>"
                embed.add_field(name="Usage:", value="The spotify command accepts words and spotify song links. "
                                                     "The user must be in a voice channel in order to use the command."
                                                     "The bot will search in the spotify API to find the requested "
                                                     "song and tries to play it from youtube if it is present on the "
                                                     "platform.")
            case "queue":
                embed.title = "Queue"
                embed.add_field(name="Usage:", value="The queue command sends an embed displaying the previously "
                                                     "added tracks that will be played.")
            case "skip":
                embed.title = "Skip"
                embed.add_field(name="Usage:", value="The skip command allows the user to skip a track when the bot "
                                                     "is playing. If nothing is in the queue then the bot will stop.")
        await ctx.send(embed=embed)

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
        await self.help_embed(ctx=ctx, command="play")

    @cog_ext.cog_subcommand(base="help",
                            subcommand_group="commands",
                            name="spotify",
                            description="spotify command",
                            guild_ids=main.bot.guid_ids)
    async def help_spotify(self, ctx):
        await self.help_embed(ctx=ctx, command="spotify")

    @cog_ext.cog_subcommand(base="help",
                            subcommand_group="commands",
                            name="queue",
                            description="queue command",
                            base_description="text commands",
                            guild_ids=main.bot.guild_ids)
    async def help_play(self, ctx):
        await self.help_embed(ctx=ctx, command="queue")

    @cog_ext.cog_subcommand(base="help",
                            subcommand_group="commands",
                            name="skip",
                            description="skip command",
                            base_description="text commands",
                            guild_ids=main.bot.guild_ids)
    async def help_play(self, ctx):
        await self.help_embed(ctx=ctx, command="skip")
