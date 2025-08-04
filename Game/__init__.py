"""
Dr. Driving Telegram Bot - Main Package

A complete driving game experience for Telegram with:
- Interactive driving gameplay
- Global rankings and leaderboards
- Admin control features
- Cross-platform support

Version: 2.1.0
"""

__version__ = "2.1.0"
__author__ = "Your Name"
__license__ = "MIT"
__all__ = ['DrDrivingBot', 'config', 'commands', 'database', 'helpers', 'static']

from .bot import DrDrivingBot
from . import (
    config,
    commands,
    database,
    helpers,
    static
)

def get_version():
    """Get the current version of the bot"""
    return __version__

def get_bot_instance():
    """Initialize and return a bot instance"""
    return DrDrivingBot()
