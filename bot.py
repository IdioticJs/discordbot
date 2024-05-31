import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
bot.balances = {}
bot.last_daily = {}

# Load balances and last daily claim times from files if they exist
if os.path.exists("balances.json"):
    with open("balances.json", "r") as f:
        bot.balances = json.load(f)

if os.path.exists("last_daily.json"):
    with open("last_daily.json", "r") as f:
        bot.last_daily = json.load(f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

def save_balances():
    with open("balances.json", "w") as f:
        json.dump(bot.balances, f)

def save_last_daily():
    with open("last_daily.json", "w") as f:
        json.dump(bot.last_daily, f)

@bot.tree.command(name="balance", description="Check your balance")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    balance = bot.balances.get(user_id, 0)
    await interaction.response.send_message(f'{interaction.user.mention}, your balance is {balance} coins.')



@bot.tree.command(name="daily", description="Claim your daily 2000 coins")
async def daily(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    now = datetime.utcnow()
    last_claim = bot.last_daily.get(user_id)
    if last_claim:
        last_claim_time = datetime.fromisoformat(last_claim)
        if now - last_claim_time < timedelta(days=1):
            next_claim_time = last_claim_time + timedelta(days=1)
            wait_time = next_claim_time - now
            hours, remainder = divmod(wait_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await interaction.response.send_message(f'You can claim your next daily reward in {hours}h {minutes}m {seconds}s.', ephemeral=True)
            return
    bot.balances[user_id] = bot.balances.get(user_id, 0) + 2000
    bot.last_daily[user_id] = now.isoformat()
    save_balances()
    save_last_daily()
    await interaction.response.send_message(f'{interaction.user.mention} claimed 2000 daily coins! Your new balance is {bot.balances[user_id]} coins.')

@bot.tree.command(name="transfer", description="Transfer coins to another user")
async def transfer(interaction: discord.Interaction, recipient: discord.User, amount: int):
    sender_id = str(interaction.user.id)
    recipient_id = str(recipient.id)
    if amount <= 0:
        await interaction.response.send_message("You must transfer a positive amount of coins.", ephemeral=True)
        return
    if bot.balances.get(sender_id, 0) < amount:
        await interaction.response.send_message("You don't have enough coins to make this transfer.", ephemeral=True)
        return
    bot.balances[sender_id] -= amount
    bot.balances[recipient_id] = bot.balances.get(recipient_id, 0) + amount
    save_balances()
    await interaction.response.send_message(f'{interaction.user.mention} transferred {amount} coins to {recipient.mention}. Your new balance is {bot.balances[sender_id]} coins.')

@bot.tree.command(name="credits", description="Show bot credits and support server")
async def credits(interaction: discord.Interaction):
    await interaction.response.send_message(
        "This bot was created by WVUWm. Join the support server here: https://discord.gg/5cPetJPVtW"
    )

bot.run('YOUR_BOT_TOKEN')
