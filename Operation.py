import datetime
import hashlib

import peewee
from peewee import fn
from playhouse.shortcuts import model_to_dict

from Database import User, Activation, Ticket, TicketPrices, Event, TicketDesign, Reports
from constants import NORMAL, OPENING, CLOSE, ESPECIAL, REPORT_X, REPORT_X_FULL, REPORT_X_EVENT, \
    REPORT_X_EVENT_FULL, TAX1, TAX2

now = datetime.datetime.today()


class POSUtils(User, Activation, Ticket, TicketPrices, Event, TicketDesign):
    def __init__(self):
        print("System Started")

    @staticmethod
    def activate_station(self):
        print("Station activated")

    @staticmethod
    def login(username, password):
        try:
            password = hashlib.sha256(password.encode()).hexdigest()
            user = User.get(User.username == username, User.password == password)
            return user
        except peewee.DoesNotExist:
            return False

    @staticmethod
    def create_user(username, password, user_type):
        password = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password=password, user_type=user_type)
        return new_user.save()

    @staticmethod
    def create_activation(user_id, station_id, activation_type, activation_start, activation_end):
        new_activation = Activation(user_id=user_id, station_id=station_id, activation_type=activation_type,
                                    activation_start=activation_start, activation_end=activation_end)

        new_activation.save()
        return Activation.get_by_id(new_activation.id)

    @staticmethod
    def create_ticket(activation_id: int, user_id: int, transaction: str, base, tax1, tax2, total, invoice_type: int,
                      ticket_count: int, ticket_price_id: int, activation_type: int):
        new_ticket = Ticket(activation_id=activation_id, user_id=user_id, ticket_count=ticket_count,
                            base=base, tax1=tax1, tax2=tax2, total=total, transaction=transaction,
                            invoice_type=invoice_type, activation_type=activation_type, ticket_price=ticket_price_id,
                            ticket_price_id=ticket_price_id, create_at=now, update_at=now)
        return new_ticket.save()

    @staticmethod
    def create_ticket_price(name, base, tax1, tax2, total, ticket_type, design="", color="#023B6D", bottomImage='',
                            topImage=''):
        new_ticket = TicketPrices(name=name, base=base, tax1=tax1, tax2=tax2, total=total, ticket_type=ticket_type,
                                  design=design, color=color, bottomImage=bottomImage, topImage=topImage)
        return new_ticket.save()

    @staticmethod
    def get_ticket_prices():
        response = []
        for ticket in TicketPrices.select():
            response.append(model_to_dict(ticket))

        return response

    @staticmethod
    def get_ticket_price(ticket_id):
        return TicketPrices.get(TicketPrices.id == ticket_id)

    @staticmethod
    def get_activation_info(activation_id):
        return Activation.get(Activation.id == activation_id)

    @staticmethod
    def get_ticket_series(ticket_type):
        query = Ticket.select().where(Ticket.activation_type == ticket_type)
        return query.count()

    @staticmethod
    def get_ticket_type_counts():
        """Retrieves the count of tickets for each activation type, returning a dictionary.

        Returns:
            dict: A dictionary where keys are activation types and values are their respective counts.
            If no tickets are found, returns an empty dictionary.
        """

        query = (Ticket.select(fn.COUNT(Ticket.activation_type).alias('count'), Ticket.activation_type)
                 .group_by(Ticket.activation_type))

        results = {row.activation_type: row.count for row in query}
        return results or {}  # Return empty dictionary if no results

    @staticmethod
    def check_difference(valor1, valor2, percent=0.2):
        # Calcula el 10% del valor1
        try:
            diez_por_ciento = valor1 * percent
        except:
            return True

        try:
            # Compara si el valor2 es igual al 10% del valor1
            if valor2 >= diez_por_ciento:
                return True
            else:
                return False
        except:
            return False

    @staticmethod
    def get_past_ticket_series(ticket_type, limit, date=datetime.date.today()):
        response = []
        query = Ticket.select(Ticket.ticket_count).where(Ticket.ticket_type == ticket_type).where(
            fn.DATE(Ticket.create_at) == date).order_by(
            peewee.fn.RAND()).limit(limit)

        for row in query:
            response.append(row.ticket_count)
        return response

    @staticmethod
    def create_event(name):
        new_event = Event(name=name)
        return new_event.save()

    @staticmethod
    def get_ticket_by_transaction(transaction):
        response = []
        for ticket in Ticket.select(Ticket.ticket_count).where(Ticket.transaction == transaction):
            response.append(dict(filter(lambda item: item[1] is not None, model_to_dict(ticket).items())))

        return response

    @staticmethod
    def get_user_list():
        response = []
        for user in User.select():
            response.append({"id": user.id, "label": user.username, "value": user.username})

        return response

    @staticmethod
    def get_report_by_user(user_id, date=datetime.date.today()):
        response = []
        user = User.get(User.id == user_id)
        ticket_count = Ticket.select().where(Ticket.user_id == user).where(
            fn.DATE(Ticket.create_at) == date).count()
        ticket_last = Ticket.select().order_by(
            Ticket.id.desc()).first().ticket_count

        query = Ticket.select(Ticket.user_id, Ticket.ticket_price_id, Ticket.ticket_type, Ticket.ticket_price,
                              fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
                              fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).where(
            Ticket.user_id == user).where(fn.DATE(Ticket.create_at) == date).group_by(Ticket.ticket_price_id).order_by(
            Ticket.create_at.asc())

        for activation in query:
            r = model_to_dict(activation)
            r["ticket_name"] = r["ticket_price_id"].get("name")
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                print("error 136")
                pass
            r["username"] = r["user_id"].get("username")
            del r["ticket_price_id"]
            del r["user_id"]
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))

        return response

    @staticmethod
    def get_report_x(report_type, activation_type=NORMAL, date=datetime.date.today()):
        response = []
        ticket_count = Ticket.select().where(
            fn.DATE(Ticket.create_at) == date).where(Ticket.activation_type == activation_type).count()
        ticket_last = Ticket.select().order_by(
            Ticket.id.desc()).first().ticket_count
        query = Ticket.select(
            fn.COUNT(Ticket.id),
            fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
            fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).where(Ticket.activation_type == activation_type).where(
            fn.DATE(Ticket.create_at) == date)
        for row in query:
            r = model_to_dict(row)
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                pass
            del r["ticket_price_id"]
            del r["user_id"]
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))
        return response

    @staticmethod
    def get_report_x_full(date=datetime.date.today()):
        response = []
        ticket_count = Ticket.select().where(
            fn.DATE(Ticket.create_at) == date).count()
        ticket_last = Ticket.select().order_by(
            Ticket.id.desc()).first().ticket_count
        query = Ticket.select(
            fn.COUNT(Ticket.id),
            fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
            fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).where(
            (Ticket.activation_type == ESPECIAL) | (Ticket.activation_type == NORMAL)).where(
            fn.DATE(Ticket.create_at) == date)
        for row in query:
            r = model_to_dict(row)
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                pass
            del r["ticket_price_id"]
            del r["user_id"]
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))
        return response

    @staticmethod
    def get_report_x_full_event(report_type=None):
        where = (Ticket.activation_type == ESPECIAL) | (Ticket.activation_type == NORMAL) if report_type == 8 else (
                Ticket.activation_type == NORMAL)
        where_count = True if report_type == 8 else (Ticket.activation_type == NORMAL)
        response = []
        ticket_count = Ticket.select().where(where_count).count()
        ticket_last = Ticket.select().order_by(
            Ticket.id.desc()).first().ticket_count
        query = Ticket.select(
            fn.COUNT(Ticket.id),
            fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
            fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).where(where)
        for row in query:
            r = model_to_dict(row)
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                pass
            del r["ticket_price_id"]
            del r["user_id"]
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))
        return response

    @staticmethod
    def get_report_by_users(date=datetime.date.today()):
        response = []
        ticket_count = Ticket.select().count()
        ticket_last = Ticket.select().order_by(
            Ticket.id.desc()).first().ticket_count
        records = Ticket.select(Ticket.user_id, Ticket.ticket_type, Ticket.ticket_price, fn.COUNT(Ticket.id),
                                fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
                                fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).group_by(Ticket.user_id).where(
            fn.DATE(Ticket.create_at) == date).order_by(Ticket.create_at.asc())

        for activation in records:
            r = model_to_dict(activation)
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                pass
            r["username"] = r["user_id"].get("username")
            del r["user_id"]
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))

        return response

    @staticmethod
    def get_report_by_ticket_type(date=datetime.date.today()):
        response = []
        for activation in Ticket.select(Ticket.ticket_type, Ticket.ticket_price,
                                        fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
                                        fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).group_by(
            Ticket.ticket_price_id).where(fn.DATE(Ticket.create_at) == date).order_by(Ticket.create_at.asc()):
            r = model_to_dict(activation)
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))

        return response

    @staticmethod
    def get_report_start_close(report_type: int, activation_type=NORMAL, date=datetime.date.today()):
        response = []
        if POSUtils.get_last_report() == report_type:
            return None

        try:
            ticket_count = Ticket.select().where(
                fn.DATE(Ticket.create_at) == date).where(Ticket.activation_type == NORMAL).count()
        except:
            ticket_count = 0

        try:
            ticket_last = Ticket.select().order_by(
                Ticket.id.desc()).first().ticket_count
        except:
            ticket_last = 0

        for activation in Ticket.select(
                fn.COUNT(Ticket.id),
                fn.SUM(Ticket.total), fn.SUM(Ticket.tax1),
                fn.SUM(Ticket.tax2), fn.SUM(Ticket.base)).where(Ticket.activation_type == activation_type).where(
            fn.DATE(Ticket.create_at) == date).order_by(
            Ticket.create_at.asc()):
            r = model_to_dict(activation)
            r["ticket_count"] = ticket_count
            r["ticket_last"] = ticket_last
            r["ticket_next"] = ticket_last + 1
            try:
                r["base"] = round(r.get("total") / ((TAX1 + TAX2) / 1 + 1), 2)
                r["tax1"] = round(r["base"] * TAX1, 2)
                r["tax2"] = round(r["base"] * TAX2, 2)
            except:
                pass
            response.append(dict(filter(lambda item: item[1] is not None, r.items())))

            new_report = Reports(activation_id=1, user_id=1, report_type=report_type)
            new_report.save()
        return response

    @staticmethod
    def report_handler(report_type, date=datetime.date.today()):
        if report_type == OPENING:
            return POSUtils.get_report_start_close(OPENING)
        if report_type == CLOSE:
            return POSUtils.get_report_start_close(CLOSE)
        if report_type == REPORT_X:
            return POSUtils.get_report_x(REPORT_X)
        if report_type == REPORT_X_FULL:
            return POSUtils.get_report_x_full()
        if report_type == REPORT_X_EVENT:
            return POSUtils.get_report_x_full_event(REPORT_X_EVENT)
        if report_type == REPORT_X_EVENT_FULL:
            return POSUtils.get_report_x_full_event(REPORT_X_EVENT_FULL)

    @staticmethod
    def get_last_report():
        try:
            return Reports.select().order_by(
                Reports.id.desc()).first().report_type
        except:
            return None

    @staticmethod
    def price_update(data):

        query = TicketPrices.update(name=data.get("priceName"), base=data.get("priceBase"), tax1=data.get("priceTax1"),
                                    tax2=data.get("priceTax2"),
                                    total=data.get("priceTotal"), ticket_type=1,
                                    design=data.get("priceDesign"), color=data.get("priceColor"),
                                    bottomImage=data.get("bottomImage"),
                                    topImage=data.get("topImage")).where(TicketPrices.id == int(data.get("priceId")))

        query.execute()
        return 200

    @staticmethod
    def print_ack(series):
        query = Ticket.update(ticket_print_count=Ticket.ticket_print_count + 1).where(Ticket.ticket_count == series)
        query.execute()
        return 200

    @staticmethod
    def get_failed_prints(user_id):
        response = []
        query = Ticket.select().where(Ticket.user_id == user_id).where(Ticket.ticket_print_count == 0)
        for row in query:
            response.append({"ticket_count": row.ticket_count, "ticket_id": row.ticket_price})
        return response

    @staticmethod
    def get_activation_list():
        response = []
        for row in Activation.select(fn.MAX(Activation.id), Activation).limit(10).group_by(Activation.user_id).order_by(
                Activation.id.desc()):
            response.append(model_to_dict(row))
        return response

    @staticmethod
    def set_activation(id_, activation_type):
        query = Activation.update(activation_type=activation_type).where(Activation.id == id_)
        query.execute()
        return 200

    @staticmethod
    def set_activation_all(activation_type):
        query = Activation.update(activation_type=activation_type)
        query.execute()
        return 200

    @staticmethod
    def get_report_dates():
        response = []
        query = Ticket.select(fn.DATE(Ticket.create_at).alias('count')).group_by(Ticket.create_at)
        for row in query.namedtuples():
            response.append(row.count.strftime("%d-%m-%Y"))
        return response

    @staticmethod
    def get_failed_prints_count(user_id):
        query = Ticket.select().where(Ticket.user_id == user_id).where(Ticket.ticket_print_count == 0).count()
        return query

    @staticmethod
    def get_activation_status(id_):
        activation = Activation.select().where(Activation.id == id_).get()
        return activation.activation_type

# x.create_ticket_price("ADULT 2", 20, 2, 22, 1)

# x.create_event("Test Event")
# print(x.get_ticket_price(1))


# print(x.sell_ticket(10, 1, True, 1, 1))
# print(x.get_ticket_prices())

# print(x.create_station("Grandma"))
# x.create_user("gerswin", "16745665", "admin")
# print(x.login("gerswin", "123"))
# x.create_activation(1, 1, 1, "2019-01-01", "2019-01-02")
# x.create_ticket(1, 1, 1, 1, 20, 20, 2, 22, 1)
# x.create_invoice(1, 1, 1, 10, 20, 20, 2, 22, 1)
#
