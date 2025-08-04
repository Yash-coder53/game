from telegram import Update
from telegram.ext import ContextTypes
from dr_driving_bot.database.models import User, GameScore, BannedUser
from dr_driving_bot.database import storage
from dr_driving_bot.config import Config
from dr_driving_bot.helpers.decorators import check_ban
from dr_driving_bot.static import messages as msg
import random

@check_ban
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
        
        await update.message.reply_text(msg.START_MESSAGE.format(user.first_name))
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@check_ban
async def my_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        with storage.db.atomic():
            scores = (GameScore.select()
                     .where(GameScore.user == user.id)
                     .order_by(GameScore.score.desc())
                     .limit(10))
            
            if not scores:
                await update.message.reply_text(msg.NO_SCORES)
                return
                
            response = msg.MY_TOP_HEADER.format(user.first_name)
            for i, score in enumerate(scores, 1):
                response += msg.SCORE_ENTRY.format(
                    rank=i,
                    score=score.score,
                    date=score.created_at.strftime("%Y-%m-%d")
                )
                
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@check_ban
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat = update.effective_chat
        with storage.db.atomic():
            # Get top 10 scores in this chat
            scores = (GameScore.select()
                     .where(GameScore.chat == chat.id)
                     .order_by(GameScore.score.desc())
                     .limit(10))
            
            if not scores:
                await update.message.reply_text(msg.NO_SCORES_CHAT)
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
                
            await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@check_ban
async def rankings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        with storage.db.atomic():
            # Get user's global rank
            user_score = (GameScore.select()
                         .where(GameScore.user == user.id)
                         .order_by(GameScore.score.desc())
                         .first())
            
            if not user_score:
                await update.message.reply_text(msg.NO_SCORES)
                return
                
            # Get global rank
            all_scores = (GameScore.select()
                         .order_by(GameScore.score.desc()))
            
            global_rank = 1
            for score in all_scores:
                if score.user == user.id:
                    break
                global_rank += 1
                
            # Get chat rank
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
