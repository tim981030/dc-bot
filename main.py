import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
token=os.getenv("token")

intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot=commands.Bot(command_prefix="!",intents=intents)

n=1

@bot.event
async def on_message(message):
    global n
    if message.author.bot:
        return

    if str(n) in message.content.lower():
        n+=1
        await message.add_reaction("✅")
        
    await bot.process_commands(message)
    
bot.run(token)