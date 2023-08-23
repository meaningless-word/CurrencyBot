import json

from bs4 import BeautifulSoup
import requests
import lxml.html
from inside_exceptions import ConversionException


class FreeCurrencyAPI:
    @staticmethod
    def fc_load_currencies():
        currencies = {}
        r = requests.get('https://freecurrencyapi.com/docs/currency-list')
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) >= 2:
                currencies[tds[0].string] = tds[1].string
        return currencies

    @staticmethod
    def fc_exchange(currencies, base_ticker, quote_ticker, amount):
        if base_ticker == quote_ticker:
            raise ConversionException('Невозможно перевести одинаковые валюты {base}.')
        try:
            base = currencies[base_ticker]
        except KeyError:
            raise ConversionException(f'Отсутствуют сведения о валюте {base_ticker}')

        try:
            quote = currencies[quote_ticker]
        except KeyError:
            raise ConversionException(f'Отсутствуют сведения о валюте {quote_ticker}')

        try:
            amount = float(amount)
        except ValueError:
            raise ConversionException(f'Передано нечисловое значение {amount}')

        r = requests.get(f'https://api.freecurrencyapi.com/v1/latest?apikey=fca_live_rCI36oRAPAQbjTGeVVGOKfbV31svSVQc9fGxbM27&currencies={base_ticker}%2C{quote_ticker}')
        j = json.loads(r.content)
        base_cost = float(j['data'][base_ticker])
        quote_cost = float(j['data'][quote_ticker])
        # поскольку бесплатная подписка на этом сайте возвращает котировки только к доллару
        # ну вот такое API попалось, придётся химичить
        result = amount * quote_cost / base_cost
        return f'{amount} {base} = {result} {quote}'
