import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Discord Token ---
load_dotenv()
token = os.getenv("token")  # 確認 Render 環境變數也是 token（小寫）

if token is None:
    raise ValueError("Discord token not found! Please set 'token' in environment variables.")

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
        await message.channel.send("wrong")

    await bot.process_commands(message)

# --- Flask Web Service for Render ---
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT"))
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)

flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# --- Run Discord Bot ---
print("Starting Discord bot...")
bot.run(token)
