import os
import discord
from discord_slash import SlashCommand
from discord.ext import commands

bot = commands.Bot(command_prefix='>')
slash = SlashCommand(bot, sync_commands=True)

bot.remove_command('help')

bot.shuffle = False
bot.announce = False
bot.playing = ""
# 2d array containing [song, channel]
bot.music_queue = []
bot.guild_ids = []


@bot.event
async def on_ready():
    for guild in bot.guilds:
        bot.guild_ids.append(guild.id)


@slash.slash(name="queue",
             description="Displays the songs in the queue",
             guild_ids=bot.guild_ids)
async def queue(ctx):
    retval = ""
    embed = discord.Embed(title="Queue", color=0x152875)
    embed.set_author(name="Slasher", icon_url="https://i.imgur.com/shZLAQk.jpg")
    for i in range(0, len(bot.music_queue)):
        retval += bot.music_queue[i][0]['title'] + "\n"
    # print(retval)
    if retval != "":
        embed.add_field(name="Songs: ", value=retval, inline=True)
        await ctx.send(embed=embed)
    else:
        embed.add_field(name="Songs: ", value="No music in queue", inline=True)
        await ctx.send(embed=embed)


@slash.slash(name="load",
             description="Load cogs",
             guild_ids=bot.guild_ids)
async def load(ctx, extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully loaded {}".format(extension))
    except ValueError:
        await ctx.send("Loading {} was unsuccesful".format(extension))


@slash.slash(name="unload",
             description="Unload cogs",
             guild_ids=bot.guild_ids)
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send("Succefully unloaded {}".format(extension))
    except ValueError:
        await ctx.send("Unloading {} was unsuccesful".format(extension))


@slash.slash(name="reload",
             description="Reload cogs",
             guild_ids=bot.guild_ids)
async def reload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully reloaded {}".format(extension))
    except ValueError:
        await ctx.send("Reloading {} was unsuccesful".format(extension))


@slash.slash(name="ping",
             description="Measures the bot latency",
             guild_ids=bot.guild_ids)
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
