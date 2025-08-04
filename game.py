import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

# Load environment variables
API_ID = int(os.getenv("API_ID", "24633463"))
API_HASH = os.getenv("API_HASH", "a2f7cd31e5017cf4fb84dd6ca2f27809")
BOT_TOKEN = os.getenv("BOT_API", "7806862913:AAHHRBDe_1FOtCV0BSXYlop17y356XOYqvo")
OWNER_ID = int(os.getenv("OWNER_ID", "7267729758"))
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "-1002325306088"))
SUDO_USERS = [int(os.getenv("SUDO_USER_ID", "7884216196"))]  # Now a list
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1002342269823"))
VERCEL_URL = os.getenv("VERCEL_URL", "")  # Your Vercel URL

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Game data storage
game_data: Dict[str, Dict] = {}  # {chat_id: {user_id: {score: int, username: str}}}
banned_users: Dict[str, List[int]] = {}  # {chat_id: [user_ids]}
globally_banned_users: List[int] = []  # [user_ids]
ban_all_enabled: Dict[str, bool] = {}  # {chat_id: bool}

# Initialize databases
def load_data():
    global game_data, banned_users, globally_banned_users, ban_all_enabled, SUDO_USERS
    try:
        with open('game_data.json', 'r') as f:
            game_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        game_data = {}
    
    try:
        with open('banned_users.json', 'r') as f:
            banned_users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        banned_users = {}
    
    try:
        with open('globally_banned_users.json', 'r') as f:
            globally_banned_users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        globally_banned_users = []
    
    try:
        with open('ban_all_enabled.json', 'r') as f:
            ban_all_enabled = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ban_all_enabled = {}
    
    try:
        with open('sudo_users.json', 'r') as f:
            SUDO_USERS = json.load(f)
            if not isinstance(SUDO_USERS, list):
                SUDO_USERS = [SUDO_USERS]
    except (FileNotFoundError, json.JSONDecodeError):
        SUDO_USERS = SUDO_USERS if isinstance(SUDO_USERS, list) else [SUDO_USERS]

def save_data():
    with open('game_data.json', 'w') as f:
        json.dump(game_data, f)
    with open('banned_users.json', 'w') as f:
        json.dump(banned_users, f)
    with open('globally_banned_users.json', 'w') as f:
        json.dump(globally_banned_users, f)
    with open('ban_all_enabled.json', 'w') as f:
        json.dump(ban_all_enabled, f)
    with open('sudo_users.json', 'w') as f:
        json.dump(SUDO_USERS, f)

load_data()

# Webhook for Vercel
@app.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    return 'Bad Request', 400

@app.route('/')
def index():
    return "Dr. Driving Bot is running!"

# Helper functions
def is_admin(chat_id: int, user_id: int) -> bool:
    if user_id in [OWNER_ID] + SUDO_USERS:
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def is_banned(chat_id: str, user_id: int) -> bool:
    return user_id in globally_banned_users or (str(chat_id) in banned_users and user_id in banned_users[str(chat_id)])

def is_ban_all_enabled(chat_id: str) -> bool:
    return str(chat_id) in ban_all_enabled and ban_all_enabled[str(chat_id)]

def log_action(action: str, details: str):
    try:
        bot.send_message(LOG_CHANNEL_ID, f"🚨 {action}\n{details}")
    except:
        pass

# Game functions
def handle_game_challenge(call: types.CallbackQuery):
    chat_id = str(call.message.chat.id)
    user_id = call.from_user.id
    
    if is_banned(chat_id, user_id):
        bot.answer_callback_query(call.id, "❌ You are banned from playing this game!", show_alert=True)
        return
    
    if is_ban_all_enabled(chat_id):
        bot.answer_callback_query(call.id, "🚫 Game is currently disabled in this chat by admin!", show_alert=True)
        return
    
    # Simulate game play
    score = calculate_score()
    
    # Update user score
    if chat_id not in game_data:
        game_data[chat_id] = {}
    if str(user_id) not in game_data[chat_id]:
        game_data[chat_id][str(user_id)] = {"score": 0, "username": call.from_user.username or call.from_user.first_name}
    
    if score > game_data[chat_id][str(user_id)]["score"]:
        game_data[chat_id][str(user_id)]["score"] = score
        
    save_data()
    
    # Respond with result
    bot.answer_callback_query(call.id, f"🏁 You scored {score} points! Your high score: {game_data[chat_id][str(user_id)]['score']}", show_alert=True)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)

def calculate_score() -> int:
    """Simulate calculating a game score"""
    return min(max(int((time.time() % 100) * 10), 500), 2500)

# Command handlers
@bot.message_handler(commands=['start'])
def start_handler(message: types.Message):
    if message.chat.type == 'private':
        if VERCEL_URL:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("🎮 Play Dr. Driving", web_app=types.WebAppInfo(url=VERCEL_URL)))
            bot.send_message(message.chat.id, "🚗 Welcome to Dr. Driving Telegram Game!\nClick below to play:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "🚗 Welcome to Dr. Driving Telegram Game!\nUse /start in groups to play.")
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🏎️ Start Driving", callback_data="start_game"))
        
        if is_banned(str(message.chat.id), message.from_user.id):
            bot.reply_to(message, "❌ You are banned from playing this game!")
            return
        
        if is_ban_all_enabled(str(message.chat.id)):
            bot.reply_to(message, "🚫 Game is currently disabled in this chat by admin!")
            return
            
        bot.reply_to(message, "🚥 Ready to play Dr. Driving?", reply_markup=markup)

@bot.message_handler(commands=['rankings'])
def show_rankings(message: types.Message):
    chat_id = str(message.chat.id)
    if chat_id not in game_data or not game_data[chat_id]:
        bot.reply_to(message, "No rankings available yet. Play a game first!")
        return
    
    sorted_users = sorted(game_data[chat_id].items(), key=lambda x: x[1]['score'], reverse=True)
    response = "🏆 Top Players:\n"
    for i, (user_id, data) in enumerate(sorted_users[:10]):
        response += f"{i+1}. {data['username']}: {data['score']} pts\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['mytop'])
def show_my_top(message: types.Message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    
    if chat_id not in game_data or user_id not in game_data[chat_id]:
        bot.reply_to(message, "You haven't played yet!")
        return
    
    score = game_data[chat_id][user_id]['score']
    total_players = len(game_data[chat_id])
    position = sorted(game_data[chat_id].items(), key=lambda x: x[1]['score'], reverse=True)
    position = [x[0] for x in position].index(user_id) + 1
    
    response = f"🏅 Your Top Score: {score} pts\n"
    response += f"📊 Rank: {position} out of {total_players}"
    bot.reply_to(message, response)

@bot.message_handler(commands=['top'])
def show_top_player(message: types.Message):
    chat_id = str(message.chat.id)
    if chat_id not in game_data or not game_data[chat_id]:
        bot.reply_to(message, "No top player yet. Play a game first!")
        return
    
    top_player = max(game_data[chat_id].items(), key=lambda x: x[1]['score'])
    response = f"👑 Top Player: {top_player[1]['username']}\n"
    response += f"🎯 Score: {top_player[1]['score']} pts"
    bot.reply_to(message, response)

# Admin commands
@bot.message_handler(commands=['addsudo'])
def add_sudo(message: types.Message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can use this command!")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a user's message to add them to sudo list.")
        return
    
    user_id = message.reply_to_message.from_user.id
    
    if user_id not in SUDO_USERS:
        SUDO_USERS.append(user_id)
        save_data()
        log_action("SUDO ADDED", f"User: {user_id}\nAdmin: {message.from_user.id}")
        bot.reply_to(message, f"✅ User [{user_id}] added to sudo list!")
    else:
        bot.reply_to(message, "User is already in sudo list!")

@bot.message_handler(commands=['rmsudo'])
def remove_sudo(message: types.Message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Only owner can use this command!")
        return
    
    if not message.reply_to_message:
        bot.reply_to_message(message, "Please reply to a user's message to remove them from sudo list.")
        return
    
    user_id = message.reply_to_message.from_user.id
    
    if user_id in SUDO_USERS:
        SUDO_USERS.remove(user_id)
        save_data()
        log_action("SUDO REMOVED", f"User: {user_id}\nAdmin: {message.from_user.id}")
        bot.reply_to(message, f"❌ User [{user_id}] removed from sudo list!")
    else:
        bot.reply_to(message, "User is not in sudo list!")

@bot.message_handler(commands=['pban'])
def personal_ban(message: types.Message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You don't have permission to use this command!")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a user's message to ban them.")
        return
    
    chat_id = str(message.chat.id)
    user_id = message.reply_to_message.from_user.id
    
    if chat_id not in banned_users:
        banned_users[chat_id] = []
    
    if user_id not in banned_users[chat_id]:
        banned_users[chat_id].append(user_id)
        save_data()
        log_action("USER BANNED", f"Chat: {chat_id}\nUser: {user_id}\nAdmin: {message.from_user.id}")
        bot.reply_to(message, f"🚫 User [{user_id}] banned from playing in this chat!")
    else:
        bot.reply_to(message, "User is already banned!")

@bot.message_handler(commands=['gban'])
def global_ban(message: types.Message):
    if message.from_user.id not in [OWNER_ID] + SUDO_USERS:
        bot.reply_to(message, "❌ Only owner and sudo users can use this command!")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a user's message to globally ban them.")
        return
    
    user_id = message.reply_to_message.from_user.id
    
    if user_id not in globally_banned_users:
        globally_banned_users.append(user_id)
        save_data()
        log_action("GLOBAL BAN", f"User: {user_id}\nAdmin: {message.from_user.id}")
        bot.reply_to(message, f"🌎 User [{user_id}] globally banned from playing!")
    else:
        bot.reply_to(message, "User is already globally banned!")

@bot.message_handler(commands=['gunban'])
def global_unban(message: types.Message):
    if message.from_user.id not in [OWNER_ID] + SUDO_USERS:
        bot.reply_to(message, "❌ Only owner and sudo users can use this command!")
        return
    
    if not message.reply_to_message:
        bot.reply_to(message, "Please reply to a user's message to globally unban them.")
        return
    
    user_id = message.reply_to_message.from_user.id
    
    if user_id in globally_banned_users:
        globally_banned_users.remove(user_id)
        save_data()
        log_action("GLOBAL UNBAN", f"User: {user_id}\nAdmin: {message.from_user.id}")
        bot.reply_to(message, f"✅ User [{user_id}] removed from global ban!")
    else:
        bot.reply_to(message, "User is not globally banned!")

@bot.message_handler(commands=['banall'])
def toggle_ban_all(message: types.Message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ You don't have permission to use this command!")
        return
    
    chat_id = str(message.chat.id)
    if chat_id not in ban_all_enabled:
        ban_all_enabled[chat_id] = True
        status = "disabled 🚫"
    else:
        ban_all_enabled[chat_id] = not ban_all_enabled[chat_id]
        status = "disabled 🚫" if ban_all_enabled[chat_id] else "enabled ✅"
    
    save_data()
    bot.reply_to(message, f"All game activity in this chat is now {status}")

# Callback handler
@bot.callback_query_handler(func=lambda call: call.data == "start_game")
def start_game_handler(call: types.CallbackQuery):
    handle_game_challenge(call)

# Run the bot
if __name__ == '__main__':
    if VERCEL_URL:
        # Set webhook for Vercel
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=f"{VERCEL_URL}/{BOT_TOKEN}")
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        # Local polling mode
        print("Bot is running in polling mode...")
        bot.infinity_polling()
