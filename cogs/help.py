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
                embed.title = "Spotify <:spotify:944554099175727124>"
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
                embed.title = "Skip :next_track:"
                embed.add_field(name="Usage:", value="The skip command allows the user to skip a track when the bot "
                                                     "is playing. If nothing is in the queue then the bot will stop.")
            case "pause":
                embed.title = "Pause :pause_button:"
                embed.add_field(name="Usage:", value="The pause command has no parameters. It tries to stop the music "
                                                     "if the bot is playing.")
            case "resume":
                embed.title = "Resume"
                embed.add_field(name="Usage:", value="The resume command resumes the music if it has been paused.")
            case "stop":
                embed.title = "Stop :stop_button:"
                embed.add_field(name="Usage:", value="The stop command stops the media playing. The next song in the "
                                                     "queue can be played once a new song is added by a play command.")
            case "leave":
                embed.title = "Leave"
                embed.add_field(name="Usage:", value="The leave command disconnects the bot from the voice channel if "
                                                     "it was in one.")
            case "clear duplicates":
                embed.title = "Clear duplicates"
                embed.add_field(name="Usage:", value="The clear duplicates command removes the duplicated songs from "
                                                     "the queue if there are any.")
            case "clear all":
                embed.title = "Clear all"
                embed.add_field(name="Usage:", value="The clear all command empties the queue completely.")
            case "np":
                embed.title = "Now Playing"
                embed.add_field(name="Usage:", value="The np command sends an embed representing the music that is "
                                                     "currently being played. If the music stopped or skipped but the "
                                                     "queue is empty than the previously played song will be sent.")
            case "subtitle":
                embed.title = "Subtitle"
                embed.add_field(name="Usage:", value="The subtitle command tries to find subtitles for the audio that "
                                                     "is being played on youtube in english.")
            case "lyrics":
                embed.title = "Lyrics"
                embed.add_field(name="Usage:", value="The lyrics command tries to find the song on genius and sends "
                                                     "back the lyrics if it succeded. Not every song will 100% have a "
                                                     "lyric. If you are sure it has but it is not available on genius "
                                                     "than the subtitle command could help.")
            case "ping":
                embed.title = "Ping"
                embed.add_field(name="Usage:", value="The ping command measures the latency from the server to the "
                                                     "client in miliseconds.")
            case _:
                embed.title = "Work in progress"
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="help",
                       description="Get info on commands.",
                       guild_ids=[940575531567546369])
    async def help(self, ctx):
        await ctx.send("Commands: ")

    @cog_ext.cog_subcommand(base="help",
                            name="play",
                            description="play command",
                            guild_ids=[940575531567546369])
    async def help_play(self, ctx):
        await self.help_embed(ctx=ctx, command="play")

    @cog_ext.cog_subcommand(base="help",
                            name="spotify",
                            description="spotify command",
                            guild_ids=[940575531567546369])
    async def help_spotify(self, ctx):
        await self.help_embed(ctx=ctx, command="spotify")

    @cog_ext.cog_subcommand(base="help",
                            name="queue",
                            description="queue command",
                            guild_ids=[940575531567546369])
    async def help_queue(self, ctx):
        await self.help_embed(ctx=ctx, command="queue")

    @cog_ext.cog_subcommand(base="help",
                            subcommand_group="commands",
                            name="skip",
                            description="skip command",
                            guild_ids=[940575531567546369])
    async def help_skip(self, ctx):
        await self.help_embed(ctx=ctx, command="skip")

    @cog_ext.cog_subcommand(base="help",
                            name="pause",
                            description="pause command",
                            guild_ids=[940575531567546369])
    async def help_pause(self, ctx):
        await self.help_embed(ctx=ctx, command="pause")

    @cog_ext.cog_subcommand(base="help",
                            name="resume",
                            description="resume command",
                            guild_ids=[940575531567546369])
    async def help_resume(self, ctx):
        await self.help_embed(ctx=ctx, command="resume")

    @cog_ext.cog_subcommand(base="help",
                            name="stop",
                            description="stop command",
                            guild_ids=[940575531567546369])
    async def help_stop(self, ctx):
        await self.help_embed(ctx=ctx, command="stop")

    @cog_ext.cog_subcommand(base="help",
                            name="leave",
                            description="leave command",
                            guild_ids=[940575531567546369])
    async def help_leave(self, ctx):
        await self.help_embed(ctx=ctx, command="leave")

    @cog_ext.cog_subcommand(base="help",
                            name="clear_dumplicates",
                            description="clear duplicates command",
                            guild_ids=[940575531567546369])
    async def help_clear_d(self, ctx):
        await self.help_embed(ctx=ctx, command="clear duplicates")

    @cog_ext.cog_subcommand(base="help",
                            name="clear_all",
                            description="clear all command",
                            guild_ids=[940575531567546369])
    async def help_clear_a(self, ctx):
        await self.help_embed(ctx=ctx, command="clear all")

    @cog_ext.cog_subcommand(base="help",
                            name="np",
                            description="np command",
                            guild_ids=[940575531567546369])
    async def help_np(self, ctx):
        await self.help_embed(ctx=ctx, command="np")

    @cog_ext.cog_subcommand(base="help",
                            name="subtitle",
                            description="subtitle command",
                            guild_ids=[940575531567546369])
    async def help_subtitle(self, ctx):
        await self.help_embed(ctx=ctx, command="subtitle")

    @cog_ext.cog_subcommand(base="help",
                            name="lyrics",
                            description="lyrics command",
                            guild_ids=[940575531567546369])
    async def help_lyrics(self, ctx):
        await self.help_embed(ctx=ctx, command="lyrics")

    @cog_ext.cog_subcommand(base="help",
                            name="ping",
                            description="ping command",
                            guild_ids=[940575531567546369])
    async def help_ping(self, ctx):
        await self.help_embed(ctx=ctx, command="ping")


def setup(bot):
    bot.add_cog(Help(bot))
