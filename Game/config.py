import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    OWNER_ID = int(os.getenv("OWNER_ID"))
    SUDO_USER_ID = int(os.getenv("SUDO_USER_ID"))
    SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID"))
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
    
    @staticmethod
    def is_owner(user_id: int) -> bool:
        return user_id == Config.OWNER_ID
    
    @staticmethod
    def is_sudo(user_id: int) -> bool:
        return user_id in (Config.OWNER_ID, Config.SUDO_USER_ID)
