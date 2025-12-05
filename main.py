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

# --- 遊戲邏輯變數 ---
n = 1
last_user_id = None  # 儲存上一次發訊息的使用者 ID
channel_id = 1446455483689992305  # 設定要監控的頻道 ID

@bot.event
async def on_message(message):
    global n
    global last_user_id

    # 忽略自己發的訊息
    if message.author.bot:
        return

    # 只監控特定頻道
    if message.channel.id != channel_id:
        return

    # 檢查同一個人不能連續發訊息
    if message.author.id == last_user_id:
        await message.channel.send("森林叫你別自幹")
        await message.add_reaction("❌")
        return
    else:
        last_user_id = message.author.id

    # 檢查訊息是否為正確數字
    if message.content.strip() == str(n):
        n += 1
        await message.add_reaction("✅")
    else:
        n = 1
        await message.add_reaction("❌")
        await message.channel.send("錯了 你將受到森林的嚴厲斥責")

    # 讓指令仍然可以運作
    await bot.process_commands(message)


# --- Flask Web Service for Render 保活 ---
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # 如果沒有設定 PORT，預設 5000
    print(f"Flask running on port {port}")
    app.run(host="0.0.0.0", port=port)

flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()


# --- Run Discord Bot ---
print("Starting Discord bot...")
bot.run(token)
