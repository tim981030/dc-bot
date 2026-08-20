import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import re

# --- Discord Token ---
load_dotenv()
print("DEBUG: 目前抓到的環境變數有:", list(os.environ.keys()))  # 加這行
token = os.getenv("token")
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
channel_id = 1446455483689992305  # 監控的頻道 ID

# 避免 on_ready 在斷線重連時重複執行還原邏輯
_state_restored = False

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
async def on_ready():
    """
    機器人啟動 / 重新連線時執行。
    往回搜尋監控頻道的訊息，找到最後一則被機器人標記 ✅ 的訊息，
    並把 n / last_user_id 還原成該狀態的下一步，避免每次重啟都歸零。
    """
    global n, last_user_id, _state_restored

    print(f"Logged in as {bot.user}")

    if _state_restored:
        return
    _state_restored = True

    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"無法取得頻道，略過狀態還原：{e}")
            return

    try:
        # 從最新往舊搜尋，最多查 500 則訊息
        async for message in channel.history(limit=500):
            if message.author.bot:
                continue

            has_check_mark = False
            for reaction in message.reactions:
                if str(reaction.emoji) == "✅" and reaction.me:
                    has_check_mark = True
                    break

            if not has_check_mark:
                continue

            value = safe_eval(message.content.strip())
            if value is None:
                continue

            try:
                restored_n = int(round(float(value)))
            except (ValueError, TypeError, OverflowError):
                continue

            n = restored_n + 1
            last_user_id = message.author.id
            print(f"狀態已還原：n = {n}, last_user_id = {last_user_id}")
            return

        # 找不到任何被 ✅ 標記的訊息，維持預設初始值
        print("找不到先前被 ✅ 標記的訊息，n 從 1 開始。")

    except Exception as e:
        print(f"還原狀態時發生錯誤，維持預設值：{e}")


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
