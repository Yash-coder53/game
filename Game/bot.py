import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from Game.config import Config
from Game.database import initialize
from Game.commands import (
    start, my_top, top, rankings,
    pban, gban, gunban, banall,
    help, about, button_handler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DrDrivingBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
        self._register_handlers()
        initialize()

    def _register_handlers(self):
        # Game commands
        self.app.add_handler(CommandHandler("start", start))
        self.app.add_handler(CommandHandler("mytop", my_top))
        self.app.add_handler(CommandHandler("top", top))
        self.app.add_handler(CommandHandler("rankings", rankings))
        
        # Admin commands
        self.app.add_handler(CommandHandler("pban", pban))
        self.app.add_handler(CommandHandler("gban", gban))
        self.app.add_handler(CommandHandler("gunban", gunban))
        self.app.add_handler(CommandHandler("banall", banall))
        
        # User commands
        self.app.add_handler(CommandHandler("help", help))
        self.app.add_handler(CommandHandler("about", about))
        
        # Button handlers
        self.app.add_handler(CallbackQueryHandler(button_handler))

    async def run(self):
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        logger.info("Dr. Driving Bot is now running!")
        await self.app.idle()
