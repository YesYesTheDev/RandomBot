import discord
from discord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Welcome Cog Loaded')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='general')
        if channel:
            await channel.send(f'Welcome to the server, {member.mention}! We are glad to have you here.')

def setup(bot):
    bot.add_cog(WelcomeCog(bot))
