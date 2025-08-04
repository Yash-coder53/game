START_MESSAGE = """
🚗 Welcome to Dr. Driving Bot, {0}! �

Drive safely and try to get the highest score!

Commands:
/start - Start the game
/mytop - Your top scores
/top - Top players in this chat
/rankings - Check your rankings
"""

PBAN_USAGE = "Usage: Reply to a user or provide user ID to ban them from playing in this chat.\nExample: /pban 123456789"
PBAN_SUCCESS = "✅ User {0} has been banned from playing in this chat."
PBAN_LOG = "🚫 User {banned} was banned in a chat by {banner}. Reason: {reason}"

GBAN_USAGE = "Usage: Reply to a user or provide user ID to globally ban them.\nExample: /gban 123456789"
GBAN_SUCCESS = "🔴 User {0} has been globally banned from the game."
GBAN_LOG = "⛔ User {banned} was globally banned by {banner}. Reason: {reason}"

GUNBAN_USAGE = "Usage: Reply to a user or provide user ID to unban them.\nExample: /gunban 123456789"
GUNBAN_SUCCESS = "🟢 User {0} has been unbanned globally."
GUNBAN_LOG = "✅ User {unbanned} was unbanned by {unbanner}"

BANALL_GROUP_ONLY = "This command can only be used in groups."
BANALL_SUCCESS = "Banned {0} members from playing in this chat."
BANALL_LOG = "Mass ban executed by {banner} in chat {chat_id}. {count} users banned."

NO_SCORES = "You don't have any scores yet. Play the game to get on the leaderboard!"
NO_SCORES_CHAT = "No scores recorded in this chat yet. Be the first to play!"

MY_TOP_HEADER = "🏆 Your Top Scores, {0}:\n\n"
SCORE_ENTRY = "{rank}. {score} points (on {date})\n"

TOP_HEADER = "🏆 Top Players in {0}:\n\n"
TOP_ENTRY = "{rank}. @{username} - {score} points\n"

RANKINGS = """
👤 Player: {user}
🌍 Global Rank: #{global_rank}
💬 Chat Rank: #{chat_rank}
🏆 Top Score: {top_score} points
"""

GLOBAL_BAN_MESSAGE = "🚫 You are globally banned from playing this game.\nReason: {reason}"
LOCAL_BAN_MESSAGE = "🚫 You are banned from playing in this chat."
RESTRICTED = "⚠️ This command is restricted to bot admins only."

ERROR = "❌ An error occurred: {error}"
