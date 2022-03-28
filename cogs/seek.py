import discord
from discord.ext import commands
from discord_slash import cog_ext
from cogs.play import Play
import discord_music_bot as main


# create a class for the cog
class Seek(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # create a seek command from cog_ext
    @cog_ext.cog_slash(name='seek', description='Seek to a specific time in the song.')  # async function for command
    async def seek(self, ctx, time):
        # send a message saying that the bot is thinking with a 1-second lifespan
        await ctx.send('The bot is thinking...', delete_after=1)
        # get the voice channel if there is one
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        # if the bot has playen a song before
        if len(main.bot.playing[ctx.guild.id]) is not 0:
            m_url = main.bot.playing[ctx.guild.id][0]['source']
            # if there is no voice channel
            if voice_channel is None:
                # send a message saying you need to be in a voice channel
                await ctx.send('You need to be in a voice channel to use this command.')
            else:
                # if there is a voice channel and the bot is not in it connect to it
                if voice == "" or voice is None:
                    voice = await main.bot.playing[ctx.guild.id][1].connect()

                else:
                    # move the bot to the voice
                    await voice.move_to(main.bot.playing[ctx.guild.id][1])
                # play the song with discord.FFmpegPCMaudio
                voice.play(discord.FFmpegPCMAudio(before_options=f'{time} -reconnect 1 -reconnect_streamed 1 '
                                                                 '-reconnect_delay_max 5',
                                                  source=m_url),
                           after=lambda e: Play(commands.Cog).play_next(ctx, voice))
                # send a message saying the bot is now playing the song
                await ctx.send(f'Now playing {main.bot.playing[ctx.guild.id][0][0]["title"]} from {time} seconds.')
        else:
            # send a message to play a song in order to seek in it
            await ctx.send('You need to play a song before you can seek in it.')


# add the cog to the bot
def setup(bot):
    bot.add_cog(Seek(bot))
