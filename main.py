import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import re

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

# --- 遊戲邏輯變數 ---
n = 57
last_user_id = None
channel_id = 1446455483689992305  # 監控的頻道 ID

# --- 數學解析安全檢查 ---
# 只允許數字、基本運算符號、括號與空格
ALLOWED_CHARS = re.compile(r"^[0-9+\-*/().\s^]+$")

def safe_eval(expr):
    """
    安全地計算數學表達式。
    支援 ^ 轉為 Python 的 ** (次方)。
    """
    # 預處理：將 ^ 替換為 Python 的次方運算符
    clean_expr = expr.replace('^', '**')
    
    # 檢查是否包含非法字元
    if not ALLOWED_CHARS.match(clean_expr):
        return None
    
    try:
        # 使用 eval 但清空內置函數，僅允許純數學運算
        result = eval(clean_expr, {"__builtins__": None}, {})
        return result
    except:
        return None

@bot.event
async def on_message(message):
    global n
    global last_user_id

    # 1. 基礎檢查：忽略機器人
    if message.author.bot:
        return

    # 2. 特殊對話回應 (不分頻道)
    if message.content.strip() == "早安":
        await message.channel.send("早安啊")
        # 這裡不 return，除非你希望「早安」不能當作數字(例如當 n=1 時輸入早安不計分)
        # 這裡通常建議 return 避免誤觸遊戲
        return

    # 3. 頻道檢查
    if message.channel.id != channel_id:
        return

    user_id = message.author.id
    content = message.content.strip()

    # 4. 嘗試解析數學公式
    calculated_value = safe_eval(content)

    # 如果解析失敗 (None)，代表這不是數字也不是數學公式，直接忽略不處理
    if calculated_value is None:
        return

    # 5. 檢查是否為「自幹」行為
    if user_id == last_user_id:
        await message.add_reaction("❌")
        await message.channel.send("森林叫你別自幹")
        n = 1
        last_user_id = None
        return

    # 6. 判斷數字是否正確
    try:
        # 使用 float 比較，處理 10/2 = 5.0 的情況
        if float(calculated_value) == float(n):
            # 數字正確
            n += 1
            last_user_id = user_id
            await message.add_reaction("✅")
        else:
            # 數字錯誤
            n = 1
            last_user_id = None
            await message.add_reaction("❌")
            await message.channel.send("錯了！你將受到森林的嚴厲斥責！")
    except (ValueError, TypeError, OverflowError):
        # 萬一運算結果出問題，忽略該訊息
        return

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

