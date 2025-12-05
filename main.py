import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ---------------------------
# 讀取 Render 環境變數 token
# ---------------------------
token = os.getenv("token")  # 必須與 Render 的 Key 完全一致
print("Loaded token:", repr(token))  # Debug：可在 Render Logs 看到是否讀到 token

if not token:
    raise ValueError("環境變數 'token' 未設定，請在 Render → Environment Variables 添加。")

# ---------------------------
# Discord Bot 設定
# ---------------------------
intents = discord.Intents.default()
intents.message_content = True
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

# ---------------------------
# Flask Web Server（給 Render 維持存活）
# ---------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render 預設會給 PORT
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()

# ---------------------------
# 啟動 Discord Bot
# ---------------------------
print("Starting Discord bot...")
bot.run(token)
