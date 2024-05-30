import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

WELCOME_CHANNEL = os.getenv('WELCOME_CHANNEL')
LEAVE_CHANNEL = os.getenv('LEAVE_CHANNEL')

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Welcome Cog Loaded')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = WELCOME_CHANNEL
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(f'Welcome to the server, {member.mention}! We are glad to have you here.')
    
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        channel_id = LEAVE_CHANNEL
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(f'We are sad to see you leave the server, {member.mention}! Please come back to us.')

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))