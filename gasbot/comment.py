from peewee import *
from gasbot.constants import *
from gasbot.secrets import *
from gasbot.drip import *
from gasbot.comments import *

db = SqliteDatabase(DB_FILE)




class Comment(Model):
    comment_id = CharField()
    comment_body = CharField()