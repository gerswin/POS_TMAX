import uuid

from Operation import POSUtils
from constants import ESPECIAL, NORMAL, CLOSE


class POSActions(POSUtils):
    def __init__(self):
        print("System Started")

    @staticmethod
    def login(username, password):
        user = POSUtils.login(username, password)
        if POSUtils.login(username, password):
            activation = POSUtils.create_activation(user.id, 1, NORMAL, "2018-01-01", "2018-01-01")
            print("User logged id", user.id, "activation", activation.id)
            return {"user_id": user.id, "user_type": user.user_type, "activation_id": activation.id}
        else:
            return False

    @staticmethod
    def sell_ticket(activation_id: int, user_id: int, qty: int, ticket_id: int, ):
        if POSUtils.get_last_report() is None:
            print("Need start report")
            return {"msg": "Necesita Reporte"}

        if POSUtils.get_last_report() == CLOSE:
            print("sales closed")
            return {"msg": "Reporte Z generado"}
        count = POSUtils.get_ticket_type_counts()
        print(count)
        if POSUtils.check_difference(count.get(0), count.get(1)):
            activation = NORMAL
        else:
            activation = ESPECIAL

        print("sell_ticket", activation_id, user_id, qty, ticket_id, "current activation", activation)
        ticket_info = POSUtils.get_ticket_price(ticket_id)
        # activation_info = POSUtils.get_activation_info(activation_id)
        transaction_id = str(uuid.uuid4())

        if activation == ESPECIAL:
            past_counter = POSUtils.get_past_ticket_series(activation, qty)
            try:
                past_counter[0]
            except:
                activation = NORMAL
        for i in range(qty):

            if activation == NORMAL:
                current_counter = POSUtils.get_ticket_series(NORMAL) + 1

            else:
                current_counter = past_counter[i]
               #current_counter = POSUtils.get_ticket_series(NORMAL) + 1

            POSUtils.create_ticket(activation_id, user_id, transaction_id, ticket_info.base, ticket_info.tax1,
                                   ticket_info.tax2, ticket_info.total, activation,
                                   current_counter,
                                   ticket_info.id, activation)
        return POSUtils.get_ticket_by_transaction(transaction_id)
