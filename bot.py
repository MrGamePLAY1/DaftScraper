import discord
from discord.ext import commands, tasks
import logging
import datetime
import pandas as pd
from dotenv import load_dotenv
import os

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

# Channel ID where bot will send messages
CHANNEL_ID = "1333186572178292737"  # Replace with your channel ID

# Read the CSV file
def read_properties_from_csv():
    try:
        # Read the CSV file
        df = pd.read_csv("all_properties.csv")
        
        # Filter properties that haven't been processed
        new_properties = df[df["processed"] == False].to_dict("records")
        
        # Log the number of new properties
        logging.info(f"Found {len(new_properties)} new properties in CSV.")
        
        return new_properties
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return []

# Mark a property as processed
def mark_property_as_processed(address):
    try:
        # Read the CSV file
        df = pd.read_csv("all_properties.csv")
        
        # Mark the property as processed
        df.loc[df["address"] == address, "processed"] = True
        
        # Save the updated CSV
        df.to_csv("all_properties.csv", index=False)
        logging.info(f"Marked property '{address}' as processed.")
    except Exception as e:
        logging.error(f"Error updating CSV file: {e}")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    check_properties.start()
    
@bot.command()
async def clear(ctx, amount=100):
    owner_id = '297460255724535808'  # Replace 'your_owner_id' with the actual owner's user ID
    logging.info(f"Command executed: !clear {amount} by {ctx.author} in {ctx.channel}")
    
    if str(ctx.message.author.id) == owner_id:
        await ctx.message.channel.purge(limit=amount)

@tasks.loop(minutes=30)  # Check every 30 minutes
async def check_properties():
    channel = bot.get_channel(int(CHANNEL_ID))
    
    # Read new properties from the CSV file
    properties = read_properties_from_csv()
    
    # Create embed for each property
    for property in properties:
        embed = discord.Embed(
            title="New Property Listed!",
            description=property["address"],
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()  # Use datetime.datetime.now()
        )
        
        embed.add_field(name="Price", value=property["price"], inline=True)
        embed.add_field(name="Details", value=", ".join(eval(property["details"])), inline=True)
        
        # Add the image URL to the embed
        if property["image_url"] and property["image_url"] != "N/A":
            embed.set_image(url=property["image_url"])
        
        await channel.send(embed=embed)
        
        # Mark the property as processed
        mark_property_as_processed(property["address"])

@bot.command()
async def properties(ctx):
    """Command to manually check properties"""
    await ctx.send("Checking for new properties...")
    await check_properties()

# Run the bot
bot.run(discord_token)  # Use the correct variable name