import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

LOG_CHANNEL = int(os.getenv('LOG_CHANNEL'))

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, interaction: discord.Interaction, action: str, member: discord.User, reason: str = None):
        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(title=action, color=discord.Color.red())
            embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=f"{interaction.user} ({interaction.user.id})", inline=False)
            await log_channel.send(embed=embed)

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        await member.ban(reason=reason)
        await interaction.response.send_message(f'{member} has been banned.')
        await self.log_action(interaction, "Ban", member, reason)

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        await member.kick(reason=reason)
        await interaction.response.send_message(f'{member} has been kicked.')
        await self.log_action(interaction, "Kick", member, reason)

    @app_commands.command(name="mute", description="Mute a member in the server.")
    @app_commands.default_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
        guild = interaction.guild
        mute_role = discord.utils.get(guild.roles, name="Muted")

        if not mute_role:
            mute_role = await guild.create_role(name="Muted")

            for channel in guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)

        await member.add_roles(mute_role, reason=reason)
        await interaction.response.send_message(f'{member} has been muted.')
        await self.log_action(interaction, "Mute", member, reason)

    @app_commands.command(name="unmute", description="Unmute a member in the server.")
    @app_commands.default_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        await member.remove_roles(mute_role)
        await interaction.response.send_message(f'{member} has been unmuted.')
        await self.log_action(interaction, "Unmute", member)

    @app_commands.command(name="unban", description="Unban a member from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = await self.bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f'{user} has been unbanned.')
        await self.log_action(interaction, "Unban", user)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
    await bot.tree.sync()

    if not bot.tree.get_command('ban'):
        bot.tree.add_command(ModerationCog.ban)
    if not bot.tree.get_command('kick'):
        bot.tree.add_command(ModerationCog.kick)
    if not bot.tree.get_command('mute'):
        bot.tree.add_command(ModerationCog.mute)
    if not bot.tree.get_command('unmute'):
        bot.tree.add_command(ModerationCog.unmute)
    if not bot.tree.get_command('unban'):
        bot.tree.add_command(ModerationCog.unban)