import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Discord Token ---
# 載入 .env 檔案中的環境變數
load_dotenv()
# 從環境變數中取得 Discord Bot Token (Render 環境變數名稱要一致)
token = os.getenv("token")

if token is None:
    # 如果找不到 token，拋出錯誤提醒使用者設定
    raise ValueError("Discord token not found! Please set 'token' in environment variables.")

# --- Discord Bot Setup ---
# 設定 Intenets 權限，確保可以讀取訊息內容和公會訊息
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

# 創建 Bot 實例，設定指令前綴為 "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 遊戲邏輯變數 (全局狀態) ---
n = 1  # 遊戲中目前需要的數字
last_user_id = None  # 上一個發送正確數字的使用者 ID
# 請將此 ID 替換為您實際要進行遊戲的頻道 ID
channel_id = 1446455483689992305

@bot.event
async def on_message(message):
    global n
    global last_user_id

    # 1. 忽略 Bot 自己的訊息
    if message.author.bot:
        return

    # 2. 忽略非指定頻道的訊息
    if message.channel.id != channel_id:
        return

    user_id = message.author.id
    content = message.content.strip()

    # 3. 檢查是否為「自幹」行為 (同一個人連續發訊息)
    if user_id == last_user_id:
        await message.add_reaction("❌")
        await message.channel.send(f"森林叫你別自幹")
        n = 1
        last_user_id = None
        return  # 結束函數，不往下判斷數字

    # 4. 檢查訊息內容是否為純數字 (修正判斷錯誤問題)
    if not content.isdigit():
        # 如果訊息不是純數字，則忽略，不觸發錯誤重置
        return

    try:
        # 將訊息內容轉換為整數
        current_n = int(content)
    except ValueError:
        return # 再次確保轉換成功

    # 5. 判斷數字是否正確
    if current_n == n:
        # 數字正確
        n += 1  # 數字遞增
        last_user_id = user_id  # 更新上一個發送者
        await message.add_reaction("✅")
        # 您可以在此處增加達到特定數字時的特殊訊息
    else:
        # 數字錯誤
        correct_n = n
        n = 1  # 數字重置為 1
        last_user_id = None  # 重置自幹判定
        await message.add_reaction("❌")
        await message.channel.send(f"錯了！你將受到森林的嚴厲斥責！")

    # 因為所有邏輯都在 on_message 處理，故不再呼叫 bot.process_commands(message)


# --- Flask Web Service for Render 保活 (Keep-Alive) ---
app = Flask("")

@app.route("/")
def home():
    # Render 會定期訪問此路由來保持 Bot 服務運行
    return "Bot is running!"

def run_flask():
    # 取得環境變數中的 PORT，預設為 5000
    port = int(os.environ.get("PORT", 5000))
    print(f"Flask running on port {port}")
    # 啟動 Flask 伺服器
    app.run(host="0.0.0.0", port=port)

# 在一個單獨的執行緒中啟動 Flask 服務，避免阻塞 Bot 的主線程
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()


# --- Run Discord Bot ---
print("Starting Discord bot...")
bot.run(token)


