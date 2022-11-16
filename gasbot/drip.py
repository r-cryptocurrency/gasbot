from peewee import *
from gasbot.constants import DB_FILE


db = SqliteDatabase(DB_FILE)


class Drip(Model):
    reddit_id = CharField()
    name = CharField()
    drip_date = DateTimeField()
    gas_type = CharField()
    
    class Meta:
            database = db 


def get_nova_drips():
    try:
        nova_drips = len(Drip.select().where(Drip.gas_type == 'nova'))
        nova_users = []
        for u in nova_drips:
            if u.name not in nova_users:
                nova_users.append(u.name)
        nova_users = len(nova_users)
        return nova_drips, nova_users
    except:
        return 0, 0

def get_matic_drips():
    try:
        matic_drips = len(Drip.select().where(Drip.gas_type == 'matic'))
        matic_users = []
        for u in matic_drips:
            if u.name not in matic_users:
                matic_users.append(u.name)
        matic_users = len(matic_users)
        return matic_drips, matic_users
    except:
        return 0, 0