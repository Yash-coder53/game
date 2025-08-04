import logging
from telegram.ext import Application, CommandHandler
from dr_driving_bot.commands import admin, game, user
from dr_driving_bot.database import storage
from dr_driving_bot.config import Config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DrDrivingBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        self._register_handlers()
        storage.initialize()

    def _register_handlers(self):
        # Game commands
        self.app.add_handler(CommandHandler("start", game.start))
        self.app.add_handler(CommandHandler("mytop", game.my_top))
        self.app.add_handler(CommandHandler("top", game.top))
        self.app.add_handler(CommandHandler("rankings", game.rankings))
        
        # Admin commands
        self.app.add_handler(CommandHandler("pban", admin.pban))
        self.app.add_handler(CommandHandler("gban", admin.gban))
        self.app.add_handler(CommandHandler("gunban", admin.gunban))
        self.app.add_handler(CommandHandler("banall", admin.banall))
        
        # Button handlers
        self.app.add_handler(CallbackQueryHandler(game.button_handler))

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Dr. Driving Bot is now running!")
        await self.app.idle()
