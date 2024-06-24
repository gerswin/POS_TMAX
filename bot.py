#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Basic example for a bot that uses inline keyboards. For an in-depth explanation, check out
 https://github.com/python-telegram-bot/python-telegram-bot/wiki/InlineKeyboard-Example.
"""
import logging

from telegram import __version__ as TG_VER
from telegram.constants import ParseMode

from Operation import POSUtils
from bot_utils import unlock_tickets
from constants import NORMAL
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
x = POSUtils()

message_ids = {}

users_availables = ["gerswin"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    print(update.message.chat)
    print(update)

    if update.message.chat.username in users_availables:
        keyboard = [
            [InlineKeyboardButton("Reimpresion", callback_data="3")],
            [InlineKeyboardButton("Reportes", callback_data="2")],
            [InlineKeyboardButton("POS", callback_data="4")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Please choose:", reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    print(update.update_id)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = []
    if query.data == "1":
        for activation in x.get_activation_list():
            keyboard.append([InlineKeyboardButton(activation.get("user_id").get("username"),
                                                  callback_data="SELECT-{}".format(activation.get("id")))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Please choose:", reply_markup=reply_markup)

    if query.data == "2":
        keyboard.append(
            [
                InlineKeyboardButton("X DIA", callback_data="REPORT-6"),
                InlineKeyboardButton("POR USUARIO", callback_data="REPORT-USERS"),
                InlineKeyboardButton("EVENTO", callback_data="REPORT-8")
            ]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("SELECCIONE EL REPORTE:", reply_markup=reply_markup)

    if query.data == "3":
        for user in x.get_user_list():
            keyboard.append([InlineKeyboardButton(user.get("label"),
                                                  callback_data="REPRINT-{}".format(user.get("id")))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona un usuario:", reply_markup=reply_markup)

    if query.data == "4":
        for price in x.get_ticket_prices():
            keyboard.append([InlineKeyboardButton(f"{price.get('name')} - {'${:,.2f}'.format(price.get('total'))}",
                                                  callback_data="POSPRICEQTY-{}".format(price.get("id")))])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona un precio:", reply_markup=reply_markup)

    if query.data.startswith("POSPRICEQTY-"):
        data = query.data.split("-")
        for qty in [1, 3, 5, 10, 20]:
            keyboard.append([InlineKeyboardButton(f"{qty}",
                                                  callback_data=f"POSPRICEBUY-{data[1]}-{qty}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona una cantidad:", reply_markup=reply_markup)

    if query.data.startswith("POSPRICEBUY-"):
        data = query.data.split("-")
        print(data)
        keyboard.append([InlineKeyboardButton("Empezar", callback_data="4")],
)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona una cantidad:", reply_markup=reply_markup)

    if query.data.startswith("REPORT-"):
        data = query.data.split("-")
        if data[1] == "USERS":
            users_list = x.get_user_list()
            for user in users_list:
                for r in x.get_report_by_user(user.get("id"), NORMAL):
                    report_html = f'''
                    <pre>
                    <b>Reporte del Sistema {user.get("label")}</b>
                    <b>Conteo de Tickets:</b> {r.get('ticket_count')}

                    <b>Base:</b> {'${:,.2f}'.format(r.get('base',0))}
                    <b>Alcaldia:</b> {'${:,.2f}'.format(r.get('tax1',0))}
                    <b>IVA:</b> {'${:,.2f}'.format(r.get('tax2',0))}
                    <b>Total:</b> {'${:,.2f}'.format(r.get('total',0))}


                    </pre>

                     Volver al inicio /start
                    '''
                    await query.message.reply_text(parse_mode=ParseMode.HTML, text=report_html)

        else:
            report = x.report_handler(int(data[1]))
            for r in report:
                report_html = f'''
                <pre>
                <b>Reporte del Sistema POS</b>

                <b>Base:</b> {'${:,.2f}'.format(r.get('base',0))}
                <b>Alcaldia:</b> {'${:,.2f}'.format(r.get('tax1',0))}
                <b>IVA:</b> {'${:,.2f}'.format(r.get('tax2',0))}
                <b>Total:</b> {'${:,.2f}'.format(r.get('total',0))}

                <b>Conteo de Tickets:</b> {r.get('ticket_count')}

                <b>Último Ticket:</b> {r.get('ticket_last')}
                <b>Próximo Ticket:</b> {r.get('ticket_next')}
                </pre>

                Volver al inicio /start
                '''

            await query.edit_message_text(parse_mode=ParseMode.HTML, text=report_html)

    if query.data.startswith("REPRINT-"):
        data = query.data.split("-")
        print("REPRINT", data)

        keyboard.append(
            [InlineKeyboardButton("1", callback_data="REPRINTACT-1-{}".format(data[1])),
             InlineKeyboardButton("2", callback_data="REPRINTACT-2-{}".format(data[1])),
             InlineKeyboardButton("3", callback_data="REPRINTACT-3-{}".format(data[1])),
             InlineKeyboardButton("5", callback_data="REPRINTACT-5-{}".format(data[1])),
             InlineKeyboardButton("9", callback_data="REPRINTACT-9-{}".format(data[1])),
             InlineKeyboardButton("10", callback_data="REPRINTACT-10-{}".format(data[1]))]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Cantidad a reimprimir:", reply_markup=reply_markup)

    if query.data.startswith("REPRINTACT-"):
        data = query.data.split("-")
        print("REPRINTACT", data)
        unlock_tickets(data[2], data[1])
        await query.edit_message_text("Entradas desbloqueadas  |  Volver al inicio /start")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("1075837064:AAHRzDiw8Gc39fd_ZauflXVOxiZvVQ6L2p4").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == "__main__":
    main()
