from peewee import *
from dr_driving_bot.database import storage

class BaseModel(Model):
    class Meta:
        database = storage.db

class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    username = CharField(null=True)
    first_name = CharField()
    last_name = CharField(null=True)
    is_globally_banned = BooleanField(default=False)
    global_ban_reason = TextField(null=True)
    banned_by = BigIntegerField(null=True)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    
class BannedUser(BaseModel):
    user = ForeignKeyField(User, backref='bans')
    reason = TextField(null=True)
    banned_by = BigIntegerField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    
class GameScore(BaseModel):
    user = ForeignKeyField(User, backref='scores')
    chat = BigIntegerField()
    score = IntegerField()
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    
    class Meta:
        indexes = (
            (('user', 'chat'), False),
        )

def create_tables():
    with storage.db:
        storage.db.create_tables([User, BannedUser, GameScore])
