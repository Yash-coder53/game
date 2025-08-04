from telegram import Update
from telegram.ext import ContextTypes
from Game.static import messages as msg

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(msg.HELP_MESSAGE)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(msg.ABOUT_MESSAGE)
