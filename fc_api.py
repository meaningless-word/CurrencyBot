from bs4 import BeautifulSoup
import requests
import lxml.html

class FreeCurrencyAPI:
    @staticmethod
    def fc_load_currenies() -> dict:
        result = {}
        r = requests.get('https://freecurrencyapi.com/docs/currency-list')
        html = r.content
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find('table')
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) >= 2:
                result[tds[1].string] = tds[0].string
        return result
