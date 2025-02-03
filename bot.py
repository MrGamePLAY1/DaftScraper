import discord
from discord.ext import commands, tasks
import logging
import datetime
import pandas as pd
from dotenv import load_dotenv
import os
import ast

# Load environment variables
load_dotenv()
discord_token = os.getenv('TOKEN')

# Logging
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
logging.basicConfig(filename='bot.log', level=logging.INFO)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Command Prefix
bot = commands.Bot(command_prefix='!', intents=intents)

# Fetch your user object when the bot starts
my_user = None

@bot.event
async def on_ready():
    global my_user
    my_user = await bot.fetch_user(os.getenv('MY_ID'))
    print(f'{bot.user} has connected to Discord!')
 # Replace with your channel ID
 
@bot.command()
async def clear(ctx, amount=100):
    """Clear messages from the channel"""
    try:
        # Check if user is authorized
        if str(ctx.author.id) == os.getenv('MY_ID'):
            # Delete messages
            deleted = await ctx.channel.purge(limit=amount + 1)
            
            # Send confirmation
            confirm_msg = await ctx.send(f'Deleted {len(deleted)-1} messages')
            await confirm_msg.delete(delay=3)
            
            # Log action
            logging.info(f"Cleared {len(deleted)-1} messages in {ctx.channel} by {ctx.author}")
        else:
            # Unauthorized user
            await ctx.send("You don't have permission to use this command", delete_after=3)
            logging.warning(f"Unauthorized clear attempt by {ctx.author}")
            
    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages")
        logging.error(f"Missing permissions to clear messages in {ctx.channel}")
    except Exception as e:
        await ctx.send("Error clearing messages")
        logging.error(f"Error in clear command: {e}")


# Run the bot
bot.run(discord_token)