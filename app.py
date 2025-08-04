#!/usr/bin/env python3
import asyncio
from dr_driving_bot.bot import DrDrivingBot

if __name__ == "__main__":
    bot = DrDrivingBot()
    asyncio.run(bot.run())
