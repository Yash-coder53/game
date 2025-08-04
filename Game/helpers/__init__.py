"""
Helpers Module - Utilities and Decorators

Provides:
- Access control decorators
- Game utility functions
- Common helper methods
"""

from .decorators import (
    restricted,
    check_ban
)

from .utils import (
    format_score,
    generate_road,
    check_collision
)

__all__ = [
    'restricted',
    'check_ban',
    'format_score',
    'generate_road',
    'check_collision'
]

# Constants for helper functions
MAX_SPEED = 3
BASE_SCORE_INCREMENT = 10
