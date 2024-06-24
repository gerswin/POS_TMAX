from peewee import *
import datetime

#db = SqliteDatabase('pos1.db')
db = MySQLDatabase('POS', user='tiquemax', password='MAgr1196', host='localhost', port=3306)

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField()
    username = CharField(unique=True)
    password = CharField()
    user_type = CharField()
    status = BooleanField(default=True)

    create_at = DateTimeField()
    update_at = DateTimeField()


class Activation(BaseModel):
    id = AutoField()
    user_id = ForeignKeyField(User)
    activation_type = IntegerField()  # 0 = legal, 1 = not legal
    activation_start = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    activation_end = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    status = BooleanField(default=True)
    create_at = DateTimeField()
    update_at = DateTimeField()





class TicketPrices(BaseModel):
    id = AutoField()
    name = CharField()
    base = DoubleField()
    tax1 = DoubleField()
    tax2 = DoubleField()
    total = DoubleField()
    ticket_type = BooleanField(default=True)  # 0 = regular , 1 = cortesia
    color = CharField()
    design = TextField()
    bottomImage = TextField()
    topImage = TextField()
    status = BooleanField(default=True)
    create_at = DateTimeField()
    update_at = DateTimeField()


class Ticket(BaseModel):
    id = AutoField()
    activation_id = ForeignKeyField(Activation)
    user_id = ForeignKeyField(User)
    transaction = CharField()
    base = DoubleField()
    tax1 = DoubleField()
    tax2 = DoubleField()
    total = DoubleField()
    ticket_type = IntegerField(default=True)  # 0 = normal, 1 = especial
    activation_type = IntegerField(default=1)  # 0 = normal, 1 = especial
    ticket_price = IntegerField(default=True)  # 0 = normal, 1 = especial
    ticket_price_id = ForeignKeyField(TicketPrices)
    ticket_count = IntegerField()
    ticket_print_count =IntegerField(default=0)
    status = BooleanField(default=True)
    create_at = DateTimeField()
    update_at = DateTimeField()

class Reports(BaseModel):
    id = AutoField()
    activation_id = ForeignKeyField(Activation)
    user_id = ForeignKeyField(User)
    report_type = IntegerField() # 0 = apertura, 1 = cierre
    create_at = DateTimeField()
    update_at = DateTimeField()

class Event(BaseModel):
    id = AutoField()
    name = CharField()
    eventDate = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
    status = BooleanField(default=True)
    create_at = DateTimeField()
    update_at = DateTimeField()


class TicketDesign(BaseModel):
    id = AutoField()
    name = CharField()
    eventDate = DateTimeField()
    status = BooleanField(default=True)
    create_at = DateTimeField()
    update_at = DateTimeField()


db.connect()
db.create_tables([Event, User, Activation, Ticket, TicketPrices, TicketDesign,Reports])
