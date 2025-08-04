from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from dr_driving_bot.database.models import User, GameScore, BannedUser
from dr_driving_bot.database import storage
from dr_driving_bot.config import Config
from dr_driving_bot.helpers.decorators import check_ban
from dr_driving_bot.static import messages as msg
import random
import time

# Game states
GAME_STATES = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        with storage.db.atomic():
            db_user, created = User.get_or_create(id=user.id)
            if created:
                db_user.username = user.username
                db_user.first_name = user.first_name
                db_user.last_name = user.last_name
                db_user.save()
        
        keyboard = [
            [InlineKeyboardButton("🚗 Start Driving", callback_data="start_driving")],
            [InlineKeyboardButton("🏆 My Scores", callback_data="my_scores"),
             InlineKeyboardButton("📊 Leaderboard", callback_data="leaderboard")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            msg.START_MESSAGE.format(user.first_name),
            reply_markup=reply_markup
        )
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    if query.data == "start_driving":
        await start_driving_game(query, context)
    elif query.data == "my_scores":
        await my_top(query, context)
    elif query.data == "leaderboard":
        await top(query, context)
    elif query.data.startswith("game_"):
        await handle_game_action(query, context)

async def start_driving_game(query, context):
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    # Initialize game state
    GAME_STATES[user_id] = {
        "score": 0,
        "distance": 0,
        "speed": 1,
        "obstacles": [],
        "start_time": time.time(),
        "message_id": query.message.message_id
    }
    
    await send_game_interface(query, context)

async def send_game_interface(query, context):
    user_id = query.from_user.id
    game_state = GAME_STATES.get(user_id)
    
    if not game_state:
        await query.edit_message_text("Game session expired. Start a new game with /start")
        return
    
    # Generate road with obstacles
    road = generate_road(game_state)
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Left", callback_data="game_left"),
         InlineKeyboardButton("🔼 Accelerate", callback_data="game_accelerate"),
         InlineKeyboardButton("➡️ Right", callback_data="game_right")],
        [InlineKeyboardButton("🛑 End Game", callback_data="game_end")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🚗 Dr. Driving\n\n"
        f"Distance: {game_state['distance']}m\n"
        f"Score: {game_state['score']}\n"
        f"Speed: {game_state['speed']}x\n\n"
        f"{road}",
        reply_markup=reply_markup
    )

def generate_road(game_state):
    # Simple ASCII road with random obstacles
    road = ""
    for i in range(5):  # 5 lines of road
        line = "|"
        for j in range(3):  # 3 lanes
            if random.random() < 0.1 and i == 2:  # Only show obstacles in middle line
                obstacle = random.choice(["🚗", "🚧", "👮"])
                line += obstacle
                game_state['obstacles'].append((i, j, obstacle))
            else:
                line += "  "
        line += "|"
        road += line + "\n"
    return road

async def handle_game_action(query, context):
    user_id = query.from_user.id
    game_state = GAME_STATES.get(user_id)
    
    if not game_state:
        await query.edit_message_text("Game session expired. Start a new game with /start")
        return
    
    action = query.data.split("_")[1]
    
    if action == "end":
        await end_game(query, context, game_state)
        return
    
    # Handle driving actions
    if action == "left":
        game_state['distance'] += 10
    elif action == "right":
        game_state['distance'] += 10
    elif action == "accelerate":
        game_state['speed'] = min(game_state['speed'] + 0.5, 3)
        game_state['distance'] += 20
    
    # Random score increment
    game_state['score'] += int(10 * game_state['speed'])
    
    # Check for collisions
    if check_collision(game_state):
        await query.edit_message_text("💥 CRASH! You hit an obstacle!\n\n"
                                    f"Final Score: {game_state['score']}")
        await save_score(user_id, query.message.chat_id, game_state['score'])
        del GAME_STATES[user_id]
        return
    
    await send_game_interface(query, context)

def check_collision(game_state):
    # 10% chance of collision when moving
    return random.random() < 0.1

async def end_game(query, context, game_state):
    user_id = query.from_user.id
    await query.edit_message_text(f"🏁 Game Over!\n\nFinal Score: {game_state['score']}")
    await save_score(user_id, query.message.chat_id, game_state['score'])
    del GAME_STATES[user_id]

async def save_score(user_id, chat_id, score):
    with storage.db.atomic():
        GameScore.create(
            user=user_id,
            chat=chat_id,
            score=score
        )

async def my_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user if isinstance(update, Update) else update.from_user
        with storage.db.atomic():
            scores = (GameScore.select()
                     .where(GameScore.user == user.id)
                     .order_by(GameScore.score.desc())
                     .limit(10))
            
            if not scores:
                text = msg.NO_SCORES
                if hasattr(update, 'edit_message_text'):
                    await update.edit_message_text(text)
                else:
                    await update.message.reply_text(text)
                return
                
            response = msg.MY_TOP_HEADER.format(user.first_name)
            for i, score in enumerate(scores, 1):
                response += msg.SCORE_ENTRY.format(
                    rank=i,
                    score=score.score,
                    date=score.created_at.strftime("%Y-%m-%d")
                )
                
            if hasattr(update, 'edit_message_text'):
                await update.edit_message_text(response)
            else:
                await update.message.reply_text(response)
    except Exception as e:
        error_msg = msg.ERROR.format(error=str(e))
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat = update.effective_chat if isinstance(update, Update) else update.message.chat
        with storage.db.atomic():
            scores = (GameScore.select()
                     .where(GameScore.chat == chat.id)
                     .order_by(GameScore.score.desc())
                     .limit(10))
            
            if not scores:
                text = msg.NO_SCORES_CHAT
                if hasattr(update, 'edit_message_text'):
                    await update.edit_message_text(text)
                else:
                    await update.message.reply_text(text)
                return
                
            response = msg.TOP_HEADER.format(chat.title)
            for i, score in enumerate(scores, 1):
                user = User.get_or_none(id=score.user)
                username = user.username if user and user.username else "Unknown"
                response += msg.TOP_ENTRY.format(
                    rank=i,
                    username=username,
                    score=score.score
                )
                
            if hasattr(update, 'edit_message_text'):
                await update.edit_message_text(response)
            else:
                await update.message.reply_text(response)
    except Exception as e:
        error_msg = msg.ERROR.format(error=str(e))
        if hasattr(update, 'edit_message_text'):
            await update.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

async def rankings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        with storage.db.atomic():
            user_score = (GameScore.select()
                         .where(GameScore.user == user.id)
                         .order_by(GameScore.score.desc())
                         .first())
            
            if not user_score:
                await update.message.reply_text(msg.NO_SCORES)
                return
                
            all_scores = (GameScore.select()
                         .order_by(GameScore.score.desc()))
            
            global_rank = 1
            for score in all_scores:
                if score.user == user.id:
                    break
                global_rank += 1
                
            chat_scores = (GameScore.select()
                          .where(GameScore.chat == chat.id)
                          .order_by(GameScore.score.desc()))
            
            chat_rank = 1
            for score in chat_scores:
                if score.user == user.id:
                    break
                chat_rank += 1
                
            response = msg.RANKINGS.format(
                user=user.first_name,
                global_rank=global_rank,
                chat_rank=chat_rank,
                top_score=user_score.score
            )
            
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))
