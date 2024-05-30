import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Loaded {extension} cog')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'Unloaded {extension} cog')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'Reloaded {extension} cog')

bot.run(TOKEN)