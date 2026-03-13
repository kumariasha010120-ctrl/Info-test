import logging
import psutil
import platform
import time
import speedtest
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Bot Token (Keep it safe!)
TOKEN = "8715339019:AAGplme4-3WhfQzZAIzcpMzJ8gBY6dwXE84"
START_TIME = time.time()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_uptime():
    delta = time.time() - START_TIME
    hours, remainder = divmod(int(delta), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    welcome_text = (
        f"👋 **Hello {user}!**\n\n"
        "🚀 **Main Render Subscription par hosted ek Professional Bot hoon.**\n"
        "system status aur speed check karne ke liye niche buttons use karein."
    )
    keyboard = [[InlineKeyboardButton("🛠️ Open Commands", callback_data='cmd')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    info_text = (
        "📊 **SERVER STATUS REPORT**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 **Host Platform:** Render (Paid)\n"
        f"🖥️ **OS:** {platform.system()} {platform.release()}\n"
        f"🐍 **Python Ver:** {platform.python_version()}\n"
        f"📦 **Library:** `python-telegram-bot`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ **Bot Uptime:** {get_uptime()}\n"
        f"🧠 **RAM Usage:** {ram.percent}% ({ram.used // (1024**2)}MB)\n"
        f"🗄️ **Disk Space:** {disk.percent}% Used\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def speed_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⚡ *Checking Server Speed... Please wait.*", parse_mode='Markdown')
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000
        upload = st.upload() / 1_000_000
        ping = st.results.ping
        
        res_text = (
            "🚀 **NETWORK SPEED TEST**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 **Download:** {download:.2f} Mbps\n"
            f"📤 **Upload:** {upload:.2f} Mbps\n"
            f"📶 **Latency:** {ping} ms\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *Result from Render Servers*"
        )
        await status_msg.edit_text(res_text, parse_mode='Markdown')
    except Exception as e:
        await status_msg.edit_text(f"❌ **Speedtest Error:** {e}")

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd_text = (
        "🛠️ **BOT CONTROL PANEL**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 `/start` - Restart interaction\n"
        "🔹 `/info` - System & Hosting details\n"
        "🔹 `/speed` - Real-time network speed\n"
        "🔹 `/cmd` - View all commands\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *UI Designed by AI Assistant*"
    )
    await update.message.reply_text(cmd_text, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("speed", speed_test))
    app.add_handler(CommandHandler("cmd", cmd_list))
    
    print("Bot is live and running...")
    app.run_polling()

