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

MY_ID = 297460255724535808

# Fetch your user object when the bot starts
my_user = None

@bot.event
async def on_ready():
    global my_user
    my_user = await bot.fetch_user(MY_ID)
    print(f'{bot.user} has connected to Discord!')
    check_properties.start()

# Channel ID where bot will send messages
CHANNEL_ID = 1333186572178292737  # Replace with your channel ID

# Read the CSV file
def read_properties_from_csv():
    try:
        df = pd.read_csv("all_properties.csv")
        
        # Ensure required columns exist
        required_columns = ["address", "price", "details", "image_url", "processed"]
        if not all(column in df.columns for column in required_columns):
            logging.error("CSV file is missing required columns.")
            return []
        
        new_properties = df[df["processed"] == False].to_dict("records")
        logging.info(f"Found {len(new_properties)} new properties in CSV.")
        return new_properties
    except FileNotFoundError:
        logging.error("CSV file not found.")
        return []
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return []

# Mark a property as processed
def mark_property_as_processed(address):
    try:
        df = pd.read_csv("all_properties.csv")
        df.loc[df["address"] == address, "processed"] = True
        df.to_csv("all_properties.csv", index=False)
        logging.info(f"Marked property '{address}' as processed.")
    except Exception as e:
        logging.error(f"Error updating CSV file: {e}")

async def send_property_embeds():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        logging.error(f"Channel with ID {CHANNEL_ID} not found.")
        return
    
    properties = read_properties_from_csv()
    for property in properties:
        embed = discord.Embed(
            title="New Property Listed!",
            description=f"Hey {my_user.mention}, a new property has been listed!\n\n**Address:** {property['address']}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Price", value=property["price"], inline=True)
        embed.add_field(name="Details", value=", ".join(ast.literal_eval(property["details"])), inline=True)
        
        if property["image_url"] and property["image_url"] != "N/A":
            embed.set_image(url=property["image_url"])
        
        await channel.send(embed=embed)
        mark_property_as_processed(property["address"])

@tasks.loop(minutes=30)
async def check_properties():
    await send_property_embeds()

@bot.command()
async def properties(ctx):
    """Command to manually check properties"""
    await ctx.send("Checking for new properties...")
    await send_property_embeds()

# Run the bot
bot.run(discord_token)