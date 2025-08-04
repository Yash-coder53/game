"""
Database Module - Core Data Management

Provides:
- Database connection and initialization
- All data models
- Storage management utilities
"""

from .storage import db, initialize
from .models import (
    BaseModel,
    User,
    BannedUser,
    GameScore,
    create_tables
)

__all__ = [
    'db',
    'initialize',
    'BaseModel',
    'User',
    'BannedUser',
    'GameScore',
    'create_tables'
]

def reset_database():
    """Drop and recreate all database tables"""
    from .models import create_tables
    with db:
        db.drop_tables([User, BannedUser, GameScore])
        create_tables()
