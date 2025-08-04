from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from dr_driving_bot.database.models import User, BannedUser
from dr_driving_bot.config import Config
from dr_driving_bot.static import messages as msg

def restricted(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not (Config.is_owner(user_id) or Config.is_sudo(user_id)):
            await update.message.reply_text(msg.RESTRICTED)
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

def check_ban(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        with storage.db.atomic():
            user = User.get_or_none(id=user_id)
            if user and user.is_globally_banned:
                await update.message.reply_text(
                    msg.GLOBAL_BAN_MESSAGE.format(reason=user.global_ban_reason or "No reason provided")
                )
                return
                
            is_locally_banned = BannedUser.select().where(
                (BannedUser.user == user_id) &
                (BannedUser.chat == chat_id)
            ).exists()
            
            if is_locally_banned:
                await update.message.reply_text(msg.LOCAL_BAN_MESSAGE)
                return
                
        return await func(update, context, *args, **kwargs)
    return wrapped
