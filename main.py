import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Discord Token ---
load_dotenv()
token = os.getenv("token")  # Render 環境變數名稱要一致

if token is None:
    raise ValueError("Discord token not found! Please set 'token' in environment variables.")

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- 遊戲邏輯變數 ---
n = 1
last_user_id = None
channel_id = 1446455483689992305  # 要監控的頻道 ID

@bot.event
async def on_message(message):
    global n
    global last_user_id

    if message.author.bot:
        return

    if message.channel.id != channel_id:
        return

    # 同一個人連續發訊息 → 自幹
    if message.author.id == last_user_id:
        await message.add_reaction("❌")
        await message.channel.send("森林叫你別自幹")
        # 自幹也要重置 n 和 last_user_id
        n = 1
        last_user_id = None
        return  # 結束函數，不往下判斷數字

    # 判斷數字是否正確
    if message.content.strip() == str(n):
        n += 1
        await message.add_reaction("✅")
    else:
        n = 1
        last_user_id = None  # 重置自幹判定
        await message.add_reaction("❌")
        await message.channel.send("錯了 你將受到森林的嚴厲斥責")
        return

    # 更新上一次發訊息者
    last_user_id = message.author.id

    await bot.process_commands(message)


# --- Flask Web Service for Render 保活 ---
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)

flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()


# --- Run Discord Bot ---
print("Starting Discord bot...")
bot.run(token)
