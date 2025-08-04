from peewee import SqliteDatabase
import os

db = SqliteDatabase('dr_driving.db')

def initialize():
    from dr_driving_bot.database.models import create_tables
    db.connect()
    create_tables()
    db.close()
