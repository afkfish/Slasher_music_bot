import discord
import discord_music_bot as main
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option


async def settings_embed(ctx):
    embed = discord.Embed(title="Settings",
                          description="The setting related to the bot",
                          color=0x152875)
    embed.set_author(name="Slasher",
                     icon_url="https://i.imgur.com/shZLAQk.jpg")
    embed.add_field(name="Prefix",
                    value="Currently the prefix is not changable due to lack of "
                          "knowledge the developer has",
                    inline=False)
    embed.add_field(name="Shuffle play :twisted_rightwards_arrows:",
                    value="Plays the songs shuffled\n\nEnabled: {}".format(
                        "True :white_check_mark:" if main.bot.shuffle else "False :x:"
                    ),
                    inline=True)
    embed.add_field(name="Announce songs :mega:",
                    value="Songs will be announced when played\n\nEnabled: {}".format(
                        "True :white_check_mark:" if main.bot.announce else "False :x:"
                    ),
                    inline=True)
    await ctx.send(embed=embed)


class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="settings",
                       guild_ids=main.bot.guild_ids)
    async def settings_(self, ctx):
        await settings_embed(ctx)

    @cog_ext.cog_subcommand(base="settings",
                            name="play",
                            description="Turns on/off shuffle playing",
                            subcommand_group="shuffle",
                            options=[
                                create_option(
                                    name="shuffle_play",
                                    description=" ",
                                    option_type=5,
                                    required=True,
                                )
                            ],
                            guild_ids=main.bot.guild_ids)
    async def settings_shuffle(self, ctx, **shuffle_play: str):
        if bool(shuffle_play["shuffle_play"]):
            main.bot.shuffle = True
        elif not bool(shuffle_play["shuffle_play"]):
            main.bot.shuffle = False
        await settings_embed(ctx)

    @cog_ext.cog_subcommand(base="settings",
                            name="songs",
                            description="Turns on/off announce",
                            subcommand_group="announce",
                            options=[
                                create_option(
                                    name="announce_songs",
                                    description=" ",
                                    option_type=5,
                                    required=True,
                                )
                            ],
                            guild_ids=main.bot.guild_ids)
    async def settings_announce(self, ctx, **announce_songs: str):
        if bool(announce_songs['announce_songs']):
            main.bot.announce = True
        elif not bool(announce_songs['announce_songs']):
            main.bot.announce = False
        await settings_embed(ctx)


def setup(bot):
    bot.add_cog(Settings(bot))
