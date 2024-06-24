import random
import string
import time
from Operation import POSUtils
from POSActions import POSActions
from constants import NORMAL, OPENING, CLOSE,ESPECIAL

# POSUtils.set_activation_all(0)

i = 0
x = POSUtils()
y = POSActions()
#x.create_user(username="gerswin", password="16745665", user_type="admin")



i = 0
while True:
    prefix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    username = "gerswin"  # "gerswin_"+prefix
    password = "16745665"

    # x.create_user(username=username , password=password, user_type="admin")

    #print(x.get_ticket_type_counts())

    #exit()
    result = next((item for item in x.get_user_list() if item['label'] == username),
                  None)  # Using a generator expression with next()
    if result:

        act = y.login(username, password)
        c = x.set_activation(act.get("activation_id"), ESPECIAL)
        x.report_handler(OPENING)
        #print("Failed", x.get_failed_prints(act.get("user_id")))
        prices = POSUtils.get_ticket_prices()[0]
        sell_ticket = POSActions.sell_ticket(act.get("activation_id"), act.get("user_id"),
                                             random.randint(0, 100), prices.get("id"))
        report_users = POSUtils.get_report_by_user((act.get("user_id")))[0].get('base')
        print(report_users)

        report_users = POSUtils.get_report_by_user((act.get("user_id")))[0].get('base')
        #print(report_users)

        report_users = POSUtils.report_handler(int(3))[0].get('base')
        #print("report x", report_users)

        report_users = POSUtils.report_handler(int(6))[0].get('base')
        #print("report x full", report_users)
        x.report_handler(CLOSE)
    else:
        raise
        print("Ayuda")
    # print(x.get_past_ticket_series(1, 3))
    #time.sleep(1)




    # x.create_ticket_price("Vip", 20, 2,2, 22, 1)
    # x.create_ticket_price("FastLane", 20, 2,2, 22, 1)
    # x.create_ticket_price("Cortesia", 20, 2, 22, 1)
    # x.create_ticket_price("General", 20, 2, 22, 1)
