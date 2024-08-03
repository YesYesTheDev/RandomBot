import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL = int(os.getenv('WELCOME_CHANNEL'))
LEAVE_CHANNEL = int(os.getenv('LEAVE_CHANNEL'))
LOG_CHANNEL = int(os.getenv('LOG_CHANNEL'))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

counting_channels = []
last_count_user = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL)
    embed = discord.Embed(title="Welcome!", description=f"Hello {member.mention}, welcome to **{member.guild.name}**!", color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)
    embed.set_footer(text="Enjoy your stay!")
    await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LEAVE_CHANNEL)
    embed = discord.Embed(title="Goodbye!", description=f"{member.mention} has left **{member.guild.name}**.", color=discord.Color.red())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)
    embed.set_footer(text="We hope to see you again!")
    await channel.send(embed=embed)

async def log_action(interaction: discord.Interaction, action: str, member: discord.User, reason: str = None):
    log_channel = bot.get_channel(LOG_CHANNEL)
    if log_channel:
        embed = discord.Embed(title=action, color=discord.Color.red())
        embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=f"{interaction.user} ({interaction.user.id})", inline=False)
        await log_channel.send(embed=embed)

@bot.tree.command(name="ban", description="Ban a member from the server.")
@app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member} has been banned.')
    await log_action(interaction, "Ban", member, reason)

@bot.tree.command(name="kick", description="Kick a member from the server.")
@app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member} has been kicked.')
    await log_action(interaction, "Kick", member, reason)

@bot.tree.command(name="mute", description="Mute a member in the server.")
@app_commands.default_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member, *, reason: str = None):
    guild = interaction.guild
    mute_role = discord.utils.get(guild.roles, name="Muted")

    if not mute_role:
        mute_role = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)

    await member.add_roles(mute_role, reason=reason)
    await interaction.response.send_message(f'{member} has been muted.')
    await log_action(interaction, "Mute", member, reason)

@bot.tree.command(name="unmute", description="Unmute a member in the server.")
@app_commands.default_permissions(manage_roles=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    await member.remove_roles(mute_role)
    await interaction.response.send_message(f'{member} has been unmuted.')
    await log_action(interaction, "Unmute", member)

@bot.tree.command(name="unban", description="Unban a member from the server.")
@app_commands.default_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    user = await bot.fetch_user(user_id)
    await interaction.guild.unban(user)
    await interaction.response.send_message(f'{user} has been unbanned.')
    await log_action(interaction, "Unban", user)

@bot.tree.command(name="welcome", description="Display the server welcome message.")
async def welcome(interaction: discord.Interaction):
    embed = discord.Embed(title="Welcome to the Server!", description="We're glad to have you here. Make sure to read the rules and enjoy your stay!", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rules", description="Display the server rules.")
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(title="Server Rules", description="1. Be respectful\n2. No spamming\n3. Follow Discord's TOS\n4. Have fun!", color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="List all available commands.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="List of available commands:", color=discord.Color.blue())
    commands = [
        ("welcome", "Display the server welcome message."),
        ("rules", "Display the server rules."),
        ("ban", "Ban a member from the server."),
        ("kick", "Kick a member from the server."),
        ("mute", "Mute a member in the server."),
        ("unmute", "Unmute a member in the server."),
        ("unban", "Unban a member from the server."),
        ("userinfo", "Get information about a member."),
        ("serverinfo", "Get information about the server."),
        ("poll", "Create a poll."),
        ("purge", "Delete a number of messages from a channel."),
        ("assignrole", "Assign a role to a member."),
        ("removerole", "Remove a role from a member."),
        ("setcountingchannel", "Set a channel for counting."),
        ("removecountingchannel", "Remove a channel from counting."),
    ]
    for name, description in commands:
        embed.add_field(name=name, value=description, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Get information about a member.")
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    embed = discord.Embed(title="User Information", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Username", value=member.name, inline=True)
    embed.add_field(name="Discriminator", value=member.discriminator, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    roles = ", ".join([role.name for role in member.roles if role.name != "@everyone"])
    embed.add_field(name="Roles", value=roles if roles else "No roles", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title="Server Information", color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server Name", value=guild.name, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Creation Date", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="poll", description="Create a poll.")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str):
    embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
    embed.add_field(name="Options", value=f"1️⃣ {option1}\n2️⃣ {option2}", inline=False)
    poll_message = await interaction.response.send_message(embed=embed)
    await poll_message.add_reaction("1️⃣")
    await poll_message.add_reaction("2️⃣")

@bot.tree.command(name="purge", description="Delete a number of messages from a channel.")
@app_commands.default_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Purged {amount} messages.", ephemeral=True)

@bot.tree.command(name="assignrole", description="Assign a role to a member.")
@app_commands.default_permissions(manage_roles=True)
async def assignrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(f"Assigned {role.name} to {member.mention}.")
    await log_action(interaction, "Assign Role", member, f"Assigned role: {role.name}")

@bot.tree.command(name="removerole", description="Remove a role from a member.")
@app_commands.default_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await interaction.response.send_message(f"Removed {role.name} from {member.mention}.")
    await log_action(interaction, "Remove Role", member, f"Removed role: {role.name}")

@bot.tree.command(name="setcountingchannel", description="Set a channel for counting.")
@app_commands.default_permissions(manage_channels=True)
async def setcountingchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if channel.id not in counting_channels:
        counting_channels.append(channel.id)
        await interaction.response.send_message(f"Counting channel set to {channel.mention}")
    else:
        await interaction.response.send_message(f"{channel.mention} is already a counting channel.")

@bot.tree.command(name="removecountingchannel", description="Remove a channel from counting.")
@app_commands.default_permissions(manage_channels=True)
async def removecountingchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if channel.id in counting_channels:
        counting_channels.remove(channel.id)
        await interaction.response.send_message(f"{channel.mention} has been removed from counting channels.")
    else:
        await interaction.response.send_message(f"{channel.mention} is not a counting channel.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.id in counting_channels:
        try:
            number = int(message.content)
            last_user_id = last_count_user.get(message.channel.id)
            
            if last_user_id == message.author.id:
                await message.delete()
                return
            
            last_count_user[message.channel.id] = message.author.id
        except ValueError:
            await message.delete()
            return
    
    await bot.process_commands(message)

bot.run(TOKEN)
