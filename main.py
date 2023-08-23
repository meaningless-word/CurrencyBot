import telebot
import json
from fc_api import FreeCurrencyAPI as fc
from telebot import types

from config import T

bot = telebot.TeleBot(T)

currencies = {
    "US Dollar": "USD",
    "Russian Ruble": "RUB",
}

from_cur = ''
to_curr = ''
quantity = 0

keyboard = types.InlineKeyboardMarkup()


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = """
Конвертер валют
Команды бота:
/load - обновление списка валют с сайта freecurrencyapi.com    
/show - отображение списка валют
/convert - пересчет суммы из одной валюты в другую
    """
    bot.reply_to(message, text)


@bot.message_handler(commands=['load'])
def load(message: telebot.types.Message):
    global currencies
    currencies = fc.fc_load_currenies()
    key_prepare()
    show(message)


@bot.message_handler(commands=['show'])
def show(message: telebot.types.Message):
    text = "доступные валюты:\n" + '\n'.join(['%s :: %s' % (key, value) for (key, value) in currencies.items()])
    bot.reply_to(message, text)


@bot.message_handler(commands=['convert'])
def convert(message: telebot.types.Message):
    #bot.send_message(message.from_user.id, "из какой?")
    bot.send_message(message.from_user.id,'из какой?', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_first_curr)


def get_first_curr(message: telebot.types.Message):
    global from_cur
    from_cur = currencies[message.text]
    text = message.text + '\nв какую?'
    bot.send_message(message.from_user.id, text)
    #bot.send_message(message.from_user.id, text, reply_markup=keyboard)
    bot.register_next_step_handler(message, get_quantity)


def get_quantity(message: telebot.types.Message):
    pass


def key_prepare():
    buttons = []
    for k, v in currencies.items():
        button = types.InlineKeyboardButton(text=v, callback_data=k)
        buttons.append(button)

        if len(buttons) % 8 == 0:
            keyboard.row(*buttons)
            buttons = []
    if len(buttons) > 0:
        keyboard.row(*buttons)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.message:
        if call.data in currencies.keys():  # call.data это callback_data, которую мы указали при объявлении кнопки
            print("Ok")
            bot.send_message(call.message.chat.id, 'Запомню : )')
    # elif call.data == "no":
    #     print("жаль")
    #     bot.send_message(call.message.chat.id, 'Зря')


key_prepare()
bot.polling()
