import telebot
from fc_api import FreeCurrencyAPI as fc
from telebot import types
from inside_exceptions import ConversionException

from config import T

bot = telebot.TeleBot(T)

currencies = {
    "USD": "US Dollar",
    "RUB": "Russian Ruble",
}

base = ''
quote = ''
amount = 0

hideBoard = types.ReplyKeyboardRemove()


@bot.message_handler(commands=['start', 'help'])
def start(message: types.Message):
    text = """
Конвертер валют
Команды бота:
/load - обновление списка валют с сайта freecurrencyapi.com    
/show - отображение списка валют
/convert - пересчет суммы из одной валюты в другую
    """
    bot.reply_to(message, text)


@bot.message_handler(commands=['load'])
def load(message: types.Message):
    global currencies
    currencies = fc.fc_load_currencies()
    show(message)


@bot.message_handler(commands=['show'])
def show(message: types.Message):
    text = "доступные валюты:\n" + '\n'.join(['%s :: %s' % (key, value) for (key, value) in currencies.items()])
    bot.reply_to(message, text)


@bot.message_handler(commands=['convert'])
def convert(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.add(*currencies.keys(), row_width=8)
    text = 'для удобства ввода воспользуйтесь контекстной клавиатурой\n'
    text += 'будут запрошены три параметра: базовая валюта, котируемая и количество средств\n'
    text += 'базовая: '
    bot.send_message(message.from_user.id, text, reply_markup=keyboard)
    bot.register_next_step_handler(message, get_first)


def get_first(message: types.Message):
    global base
    base = message.text
    text = message.text + '\nкотируемая: '
    bot.send_message(message.from_user.id, text)
    bot.register_next_step_handler(message, get_second)


def get_second(message: types.Message):
    global quote
    quote = message.text
    text = message.text + '\nколичество: '
    bot.send_message(message.from_user.id, text, reply_markup=hideBoard)
    bot.register_next_step_handler(message, get_third)


def get_third(message: types.Message):
    global amount
    amount = message.text

    try:
        total_base = fc.fc_exchange(currencies, base, quote, amount)
    except ConversionException as e:
        bot.reply_to(message, f'Ошибка пользователя:\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        bot.send_message(message.chat.id, total_base)


bot.polling()
