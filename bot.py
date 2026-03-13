import logging
import psutil
import platform
import time
import threading
import speedtest
import os
import json
import socket
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIGURATION ---
TOKEN = "8715339019:AAGplme4-3WhfQzZAIzcpMzJ8gBY6dwXE84"
START_TIME = time.time()
DB_FILE = "users.json"

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DATABASE LOGIC ---
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f: json.dump(users, f)

# --- UTILS ---
def get_uptime():
    delta = time.time() - START_TIME
    h, r = divmod(int(delta), 3600)
    m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def get_size(bytes):
    for unit in ['', 'K', 'M', 'G', 'T']:
        if bytes < 1024: return f"{bytes:.2f}{unit}B"
        bytes /= 1024

# --- 🌐 PROFESSIONAL WEB JSON INTERFACE ---
class JsonApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Data to show on the Website
        server_data = {
            "status": "Online",
            "bot_name": "Premium Elite Bot",
            "deployment": {
                "platform": "Render.com",
                "tier": "Paid/Subscription",
                "region": "Singapore (SG-1)",
                "uptime": get_uptime()
            },
            "server_health": {
                "cpu_usage": f"{psutil.cpu_percent()}%",
                "ram_usage": f"{psutil.virtual_memory().percent}%",
                "disk_free": get_size(psutil.disk_usage('/').free)
            },
            "developer": {
                "name": "Adarsh",
                "github": "atul0930976-cpu",
                "api_version": "3.0.1"
            },
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(server_data, indent=4).encode())

def run_web_server():
    # Render binds to port 10000
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), JsonApiHandler)
    logger.info(f"Web JSON Server started on port {port}")
    server.serve_forever()

# --- ⌨️ KEYBOARDS ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 System Stats", callback_data='stats'),
         InlineKeyboardButton("🚀 Network Speed", callback_data='speed')],
        [InlineKeyboardButton("💻 HW Specs", callback_data='hw'),
         InlineKeyboardButton("🛠️ Commands", callback_data='cmds')],
        [InlineKeyboardButton("🌐 Visit API Site", url="https://info-test-1.onrender.com")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')]])

# --- 🎮 BOT HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    text = (
        f"👑 **ELITE DASHBOARD V3**\n\n"
        f"Welcome **{user.first_name}**!\n"
        "Aapka bot Render Subscription par safely host ho chuka hai.\n\n"
        "🔴 **Server:** Live\n"
        "🟢 **Database:** Connected\n"
        "🔵 **Web API:** Active\n\n"
        "Niche diye gaye options use karein:"
    )
    await update.message.reply_text(text, reply_markup=get_main_menu(), parse_mode='Markdown')

async def stats_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    text = (
        "📊 **LIVE SERVER METRICS**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ **Uptime:** {get_uptime()}\n"
        f"🧠 **RAM:** {ram.percent}% ({get_size(ram.used)}/{get_size(ram.total)})\n"
        f"🔥 **CPU:** {psutil.cpu_percent()}%\n"
        f"📁 **Disk:** {disk.percent}% ({get_size(disk.free)} free)\n"
        f"👥 **Users:** {len(load_users())}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    if update.callback_query: await update.callback_query.message.edit_text(text, reply_markup=get_back_btn(), parse_mode='Markdown')
    else: await update.message.reply_text(text, parse_mode='Markdown')

async def speed_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    msg = await query.message.edit_text("⚡ *Testing Network... Please wait.*", parse_mode='Markdown')
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        d, u = st.download()/1e6, st.upload()/1e6
        res = (
            "🚀 **SPEEDTEST RESULTS**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📥 **Download:** {d:.2f} Mbps\n"
            f"📤 **Upload:** {u:.2f} Mbps\n"
            f"📶 **Ping:** {st.results.ping} ms\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        await msg.edit_text(res, reply_markup=get_back_btn(), parse_mode='Markdown')
    except: await msg.edit_text("❌ Speedtest Error.", reply_markup=get_back_btn())

async def hw_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💻 **HARDWARE ARCHITECTURE**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"🖥️ **CPU:** {platform.processor()}\n"
        f"⚙️ **Cores:** {psutil.cpu_count(logical=True)} Threads\n"
        f"🌍 **System:** {platform.system()} {platform.machine()}\n"
        f"🐍 **Python:** v{platform.python_version()}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await update.callback_query.message.edit_text(text, reply_markup=get_back_btn(), parse_mode='Markdown')

async def cmd_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📜 **COMMAND DIRECTORY**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 `/start` - Home Dashboard\n"
        "🔹 `/stats` - Hardware Usage\n"
        "🔹 `/speed` - Run Speedtest\n"
        "🔹 `/hw` - System Specs\n"
        "🔹 `/cmd` - All Commands\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    if update.callback_query: await update.callback_query.message.edit_text(text, reply_markup=get_back_btn(), parse_mode='Markdown')
    else: await update.message.reply_text(text, parse_mode='Markdown')

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'stats': await stats_logic(update, context)
    elif data == 'speed': await speed_logic(update, context)
    elif data == 'hw': await hw_logic(update, context)
    elif data == 'cmds': await cmd_logic(update, context)
    elif data == 'main_menu':
        await query.message.edit_text("👑 **ELITE DASHBOARD V3**\nChoose an option:", reply_markup=get_main_menu(), parse_mode='Markdown')

# --- MAIN START ---
if __name__ == '__main__':
    # 1. Start Web Server in Thread
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # 2. Start Bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Register Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_logic))
    app.add_handler(CommandHandler("speed", speed_logic))
    app.add_handler(CommandHandler("cmd", cmd_logic))
    
    # Register Buttons
    app.add_handler(CallbackQueryHandler(button_router))
    
    print("Bot & JSON Site are Online!")
    app.run_polling()
    
