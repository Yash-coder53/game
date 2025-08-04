from telegram import Update
from telegram.ext import ContextTypes
from Game.database.models import User, BannedUser
from Game.database import storage
from Game.config import Config
from Game.helpers.decorators import restricted
from Game.static import messages as msg

@restricted
async def pban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not update.message.reply_to_message:
        await update.message.reply_text(msg.PBAN_USAGE)
        return
    
    try:
        user_id = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        with storage.db.atomic():
            user, created = User.get_or_create(id=user_id)
            BannedUser.create(user=user, reason=reason, banned_by=update.effective_user.id)
            
        await update.message.reply_text(msg.PBAN_SUCCESS.format(user_id))
        await context.bot.send_message(
            Config.LOG_CHANNEL_ID,
            msg.PBAN_LOG.format(
                banner=update.effective_user.id,
                banned=user_id,
                reason=reason
            )
        )
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@restricted
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not update.message.reply_to_message:
        await update.message.reply_text(msg.GBAN_USAGE)
        return
    
    try:
        user_id = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        with storage.db.atomic():
            user, created = User.get_or_create(id=user_id)
            user.is_globally_banned = True
            user.global_ban_reason = reason
            user.banned_by = update.effective_user.id
            user.save()
            
        await update.message.reply_text(msg.GBAN_SUCCESS.format(user_id))
        await context.bot.send_message(
            Config.LOG_CHANNEL_ID,
            msg.GBAN_LOG.format(
                banner=update.effective_user.id,
                banned=user_id,
                reason=reason
            )
        )
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@restricted
async def gunban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not update.message.reply_to_message:
        await update.message.reply_text(msg.GUNBAN_USAGE)
        return
    
    try:
        user_id = int(context.args[0]) if context.args else update.message.reply_to_message.from_user.id
        
        with storage.db.atomic():
            user = User.get_or_none(id=user_id)
            if user:
                user.is_globally_banned = False
                user.global_ban_reason = None
                user.banned_by = None
                user.save()
                
                # Also remove from local bans
                BannedUser.delete().where(BannedUser.user == user).execute()
            
        await update.message.reply_text(msg.GUNBAN_SUCCESS.format(user_id))
        await context.bot.send_message(
            Config.LOG_CHANNEL_ID,
            msg.GUNBAN_LOG.format(
                unbanner=update.effective_user.id,
                unbanned=user_id
            )
        )
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))

@restricted
async def banall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text(msg.BANALL_GROUP_ONLY)
        return
    
    try:
        members_count = 0
        async for member in context.bot.get_chat_members(update.effective_chat.id):
            if member.user.is_bot:
                continue
                
            with storage.db.atomic():
                user, created = User.get_or_create(id=member.user.id)
                BannedUser.create(user=user, reason="Mass ban", banned_by=update.effective_user.id)
                members_count += 1
                
        await update.message.reply_text(msg.BANALL_SUCCESS.format(members_count))
        await context.bot.send_message(
            Config.LOG_CHANNEL_ID,
            msg.BANALL_LOG.format(
                banner=update.effective_user.id,
                chat_id=update.effective_chat.id,
                count=members_count
            )
        )
    except Exception as e:
        await update.message.reply_text(msg.ERROR.format(error=str(e)))
