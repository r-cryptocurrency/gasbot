from gasbot.user import User
from peewee import *
from gasbot.constants import *
from gasbot.secrets import *

db = SqliteDatabase(DB_FILE)


class Drip(Model):
    reddit_id = CharField()
    user = ForeignKeyField(User, backref='drips')
    drip_date = DateTimeField()
    gas_type = CharField()
    amount = FloatField()
    
    class Meta:
            database = db 


def get_nova_drips():
    # try:
        data = Drip.select().where(Drip.gas_type == 'nova')
        nova_drips = len(data)
        nova_users = []
        nova_amt = 0
        for u in data:
            nova_amt += u.amount
            if u.user.name not in nova_users:
                nova_users.append(u.user.name)
        nova_users = len(nova_users)
        return nova_drips, nova_users, nova_amt
    #except:
    #    return 0, 0

def get_matic_drips():
    #try:
        data = Drip.select().where(Drip.gas_type == 'matic')
        matic_drips = len(data)
        matic_users = []
        matic_amt = 0
        for u in data:
            matic_amt += u.amount
            if u.user.name not in matic_users:
                matic_users.append(u.user.name)
        matic_users = len(matic_users)
        return matic_drips, matic_users, matic_amt
    #except:
    #    return 0, 0