import os
from discord_slash import SlashCommand
from discord.ext import commands

bot = commands.Bot(command_prefix='>')
slash = SlashCommand(bot, sync_commands=True)

bot.remove_command('help')

bot.shuffle = False
bot.announce = False
bot.playing = ""


@slash.slash(name="load",
             description="Load cogs",
             guild_ids=[663825004256952342])
async def load(ctx, extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully loaded {}".format(extension))
    except:
        await ctx.send("Loading {} was unsuccesful".format(extension))


@slash.slash(name="unload",
             description="Unload cogs",
             guild_ids=[663825004256952342])
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send("Succefully unloaded {}".format(extension))
    except:
        await ctx.send("Unloading {} was unsuccesful".format(extension))


@slash.slash(name="reload",
             description="Reload cogs",
             guild_ids=[663825004256952342])
async def reload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully reloaded {}".format(extension))
    except:
        await ctx.send("Reloading {} was unsuccesful".format(extension))


@slash.slash(name="ping",
             description="Measures the bot latency",
             guild_ids=[663825004256952342])
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency*1000)}ms")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# start the bot with our token
bot.run("NzgyODk3NzcxNzQ5MzEwNDg0.X8S4Xg.YV5fFiOvRot6ab-dHKPZUTI6Eb8")
