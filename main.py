import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Discord Token ---
load_dotenv()
token = os.getenv("token")

if token is None:
    raise ValueError("Discord token not found! Please set 'token' in environment variables.")

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 記數變數
n = 1

@bot.event
async def on_message(message):
    global n

    # 忽略機器人訊息
    if message.author.bot:
        return

    # 限定頻道
    if message.channel.id != 1446455483689992305 and message.channel.id != 1446132825127387288:
        return

    content = message.content

    # 判斷數字順序
    if str(n) == content:
        n += 1
        await message.add_reaction("✅")

    else:
        n = 1
        await message.add_reaction("❌")
        await message.channel.send("錯了 你將受到森林的嚴厲斥責")

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


