import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Discord Token ---
load_dotenv()
token = os.getenv("token")

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
n = 1

@bot.event
async def on_message(message):
    global n
    if message.author.bot:
        return

    if str(n) in message.content.lower():
        n += 1
        await message.add_reaction("✅")
    else:
        n = 1
        await message.add_reaction("❌")
        await message.channel.send(f"wrong")

    await bot.process_commands(message)

# --- Flask Web Service for Render ---
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Run Flask in a separate thread
Thread(target=run_flask).start()

# Run Discord Bot
bot.run(token)
