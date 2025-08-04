#!/usr/bin/env python3
import asyncio
import platform
import sys
from Game.bot import DrDrivingBot

def get_platform_config():
    system = platform.system().lower()
    if system == 'windows':
        return {'loop': asyncio.ProactorEventLoop()}
    return {}

if __name__ == "__main__":
    config = get_platform_config()
    
    if 'loop' in config:
        asyncio.set_event_loop(config['loop'])
    
    try:
        bot = DrDrivingBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
