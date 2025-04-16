import os
import discord
import datetime
from docx import Document

print("🔁 起動開始")

# ==== 環境変数 ====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
print("🔐 DISCORD_TOKEN の読み込み:", "OK" if DISCORD_TOKEN else "❌ None")

# ==== Discord Intents ====
intents = discord.Intents.default()
intents.message_content = True
print("⚙️ Intents 設定完了")

client = discord.Client(intents=intents)
print("🧠 Discordクライアント作成完了")

# ==== チャンネル制限 ====
TARGET_CHANNEL_ID = 1345725867107815434  # ← チャンネルIDを差し替えて！

# ==== 月ごとのファイル名を作成 ====
def get_monthly_filename(prefix, extension):
    now = datetime.datetime.now()
    return f"{prefix}_{now.year}_{now.month:02d}.{extension}"

# ==== メッセージ保存処理 ====
def save_message(user, content):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    txt_filename = get_monthly_filename("summaries", "txt")

    with open(txt_filename, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {user}: {content}\n")

# ==== summaries_YYYY_MM.txt → summary_YYYY_MM.docx に変換 ====
def convert_txt_to_docx():
    txt_filename = get_monthly_filename("summaries", "txt")
    docx_filename = get_monthly_filename("summary", "docx")

    if not os.path.exists(txt_filename):
        return None

    document = Document()
    document.add_heading("月次メッセージログ", level=1)

    with open(txt_filename, "r", encoding="utf-8") as f:
        for line in f:
            document.add_paragraph(line.strip())

    document.save(docx_filename)
    return docx_filename

# ==== Bot起動時 ====
@client.event
async def on_ready():
    print(f"✅ Bot 起動完了: {client.user}")

# ==== メッセージ処理 ====
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != TARGET_CHANNEL_ID:
        return

    if message.content.strip() == "!send-summary":
        docx_file = convert_txt_to_docx()
        if docx_file:
            await message.channel.send("📄 今月のメッセージまとめです：", file=discord.File(docx_file))
        else:
            await message.channel.send("⚠️ 今月の記録ファイルが見つかりません。")
    else:
        save_message(message.author.display_name, message.content)
        print(f"📝 保存: {message.author.display_name}: {message.content}")
try:
    client.run(DISCORD_TOKEN)
except Exception as e:
    print("❌ 起動エラー:", e)