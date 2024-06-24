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
x.create_user(username="gerswin", password="16745665", user_type="admin")
x.create_user(username="Kathy", password="15639193", user_type="admin")
x.create_user(username="Jaserliz", password="26502408", user_type="admin")
x.create_user(username="Maury", password="27094618", user_type="admin")
x.create_user(username="Yasmely", password="13660300", user_type="admin")
x.create_user(username="Renny", password="17107079", user_type="admin")
x.create_user(username="Alix", password="16745948", user_type="admin")
