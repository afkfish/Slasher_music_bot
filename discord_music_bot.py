import discord
import json
from discord_slash import SlashCommand
from discord.ext import commands

bot = commands.Bot(command_prefix='>')
slash = SlashCommand(bot, sync_commands=True)

bot.remove_command('help')

with open("secrets.json", "r") as file:
    application_key = json.load(file)["discord"]["app_key"]

modules = [
    'navigation',
    'play',
    'settings',
    'spotify',
    'help'
]


def bot_shuffle(guildid):
    with open('./settings/settings.json', 'r') as f:
        data = json.load(f)
    return bool(data[str(guildid)]['shuffle'])


def bot_announce(guildid):
    with open('./settings/settings.json', 'r') as f:
        data = json.load(f)
    return bool(data[str(guildid)]['announce'])


bot.playing = {}
bot.music_queue = {}
bot.guild_ids = []


@bot.event
async def on_ready():
    print("ready")
    with open('./settings/settings.json', 'r') as f:
        data = json.load(f)
    for guild in bot.guilds:
        if guild.id not in data:
            data.update({str(guild.id): {'announce': False, 'shuffle': False}})
        bot.guild_ids.append(guild.id)
        bot.music_queue[guild.id] = []
        bot.playing[guild.id] = ''
    with open('./settings/settings.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.event
async def on_guid_join(guild):
    with open('./settings/settings.json', 'r') as f:
        data = json.load(f)
    data.update({str(guild.id): {'announce': False, 'shuffle': False}})
    bot.guild_ids.append(guild.id)
    bot.music_queue[guild.id] = []
    bot.playing[guild.id] = ''
    with open('./settings/settings.json', 'w') as f:
        json.dump(data, f, indent=4)


@slash.slash(name="load",
             description="Load cogs",
             guild_ids=[940575531567546369])
async def load(ctx, extension):
    try:
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully loaded {}".format(extension))
    except Exception as ex:
        print('Failed to load mod {0}\n{1}: {2}'.format(cog, type(ex).__name__, ex))
        await ctx.send("Reloading {} was unsuccesful\nError: {}\n{}: {}".format(extension, cog, type(ex).__name__, ex))


@slash.slash(name="unload",
             description="Unload cogs",
             guild_ids=[940575531567546369])
async def unload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        await ctx.send("Succefully unloaded {}".format(extension))
    except Exception as ex:
        print('Failed to load mod {0}\n{1}: {2}'.format(cog, type(ex).__name__, ex))
        await ctx.send("Reloading {} was unsuccesful\nError: {}\n{}: {}".format(extension, cog, type(ex).__name__, ex))


@slash.slash(name="reload",
             description="Reload cogs",
             guild_ids=[940575531567546369])
async def reload(ctx, extension):
    try:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send("Succefully reloaded {}".format(extension))
    except Exception as ex:
        print('Failed to load mod {0}\n{1}: {2}'.format(cog, type(ex).__name__, ex))
        await ctx.send("Reloading {} was unsuccesful\nError: {}\n{}: {}".format(extension, cog, type(ex).__name__, ex))


@slash.slash(name="ping",
             description="Measures the bot latency",
             guild_ids=bot.guild_ids)
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


for cog in modules:
    try:
        bot.load_extension(f'cogs.{cog}')
    except Exception as e:
        print('Failed to load mod {0}\n{1}: {2}'.format(cog, type(e).__name__, e))

# start the bot with token
bot.run(application_key)
