from datetime import datetime
from datetime import timedelta

from escpos.printer import Network

from Database import Ticket


def format_line(left_text, right_text, total_length=45):
    """
    Formats a line to a specific length by padding with spaces.

    :param left_text: The text to be placed on the left.
    :param right_text: The text to be placed on the right.
    :param total_length: The total length of the line, default is 45 characters.
    :return: The formatted line.
    """
    # Calculate the number of spaces needed
    spaces_needed = total_length - len(left_text) - len(str(right_text))

    # Ensure that spaces_needed is not negative
    spaces_needed = max(spaces_needed, 0)

    # Create the line with the right amount of padding
    return f"{left_text}{' ' * spaces_needed}{right_text}\n"

p = Network("192.168.200.128") # Asegúrate de que esta es la dirección IP correcta de tu impresora
def print_start(date,last,next,count):
    # Imprimir el encabezado del repordbte
    p.set(align='center')
    p._raw(b'\x1d\x21\x11')
    # Print text with the new font size
    p.text("Acta de inicio\n")
    # Reset to default font size
    # 0x00 resets the size to normal
    p._raw(b'\x1d\x21\x00')
    p.text("\n")
    p.set(align='left')
    p.text("Usuario: Admin\n")
    p.text(f"{format_line('Tickets Impresos', count)}")
    p.text(f"{format_line('Tickets Anterior', last)}")
    p.text(f"{format_line('Tickets Siguiente', next)}")

    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.set(align='center')
    p.text(f"{date.strftime('%Y-%m-%d')}\n")
    p.text("\n")
    p.text("------------------------------------------------\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text("\n")
    p.text(format_line("Alcaldia","Empresario"))
    p.cut()




# Obtener la fecha actual y la fecha del día anterior
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
yesterday = today - timedelta(days=1)

# ID más bajo del día actual
lowest_id_today = (Ticket
                   .select()
                   .where((Ticket.create_at >= today) & (Ticket.create_at < (today + timedelta(days=1))))
                   .order_by(Ticket.id.asc())
                   .first())


# ID más alto del día anterior
highest_id_yesterday = (Ticket
                        .select()
                        .where((Ticket.create_at >= yesterday) & (Ticket.create_at < today))
                        .order_by(Ticket.id.desc())
                        .first())

if highest_id_yesterday and lowest_id_today:
    print("------")
    print(f"Hoy es: {today.strftime('%Y-%m-%d')}")
    print(f"El ID más alto de ayer es: {highest_id_yesterday.ticket_count}")
    print(f"El ID más bajo de hoy es: {lowest_id_today.ticket_count}")
    print("------")
    print_start(today,highest_id_yesterday.ticket_count,highest_id_yesterday.ticket_count +1, 0)
