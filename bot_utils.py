from peewee import fn
from datetime import datetime
from Database import Ticket

# Obtiene la fecha actual
today = datetime.now().date()


def unlock_tickets(user_id, limit):
    print("unlock", user_id,limit)
    # Selecciona aleatoriamente 10 registros de Ticket donde user_id sea 1 y el día sea hoy
    tickets = (Ticket
               .select()
               .where((Ticket.user_id == (user_id)) & (fn.date(Ticket.create_at) == today))
               .order_by(fn.Rand())
               .limit(int(limit)))

    # Actualiza el ticket_count a 0 para los registros seleccionados
    for ticket in tickets:
        print(ticket.id)
        ticket.ticket_print_count = 0
        ticket.save()
