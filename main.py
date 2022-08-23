import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import time

class Site:
    """
    Основной класс Site, который представляет общий функционал классов-наследников
    """

    def __init__(self, search_item):
        """
        Конструктор класса
        :param search_item: поисковый запрос - название запроса (например, кроссовки nike)
        """

    def _get_responce(self, url, params, headers):
        """
        Сделать get-запрос к сайту
        :return: ответ сайта
        """
        responce = requests.get(url=url,
                                params=params,
                                headers=headers)
        if responce.status_code == 200:
            return responce
        else:
            assert "Bad status code"

    def _parse_html(self, html):
        """
        Распарсить html через BeautifulSoup
        :param html: html в чистом виде без отсутоп и табуляций
        :return: html с выполненными отступами и табуляциями
        """
        return BeautifulSoup(html, "lxml")

    def _to_count_items(self, html, tag, attributes):
        """
        Подсчитать количество найденных предметов
        :param html: html
        :param tag: тег из html
        :param attributes: атрибуты тега
        :return: число типа int
        """
        pass

    def _get_nums(self, string):
        """
        Найти подряд идущие цифры из строки
        :param string: строка, из которой необходимо забрать цифры
        :return: список таких цифр
        """
        return re.findall('\d+', string)

    def _to_count_pages(self, count_items, items_on_page):
        """
        Подсчиытвает количество страниц в поиске
        :param count_items: Количество найденных предметов
        :param items_on_page: Количество предметов на 1 странице
        :return:
        """
        if count_items > items_on_page:
            pages = count_items / items_on_page
            if type(pages) is float:
                pages = int(pages) + 1
        else:
            pages = 1
        return pages

    def _correct_value_price(self):
        """
        Распарсить цену товара
        """
        pass

    def _get_links_prices(self):
        """
        Получить списки из ссылок и стоимости товаров
        :return: списки из ссылок и стоимости
        """
        pass

    def _to_zip(self, links, prices):
        """
        Создать соответствующую пару типа "ссылка на товар - его цена"
        :param links: список ссылок на товары
        :param prices: список цен на товары
        :return: Список пар типа "ссылка на товар - его цена"
        """
        return [(links[i], prices[i]) for i in range(len(links))]

    def _to_go(self):
        """
        Выполнить все реализованные методы
        :return: список кортежей из ссылок и стоимостей на товар, остортированный по убыванию цен
        """
        pass

class Asos(Site):
    """
    Сайт asos.com
    Имеет один открый метод to_go(), который выполняет все закрытые методы класса
    """

    def __init__(self, search_item):
        self._url = "https://www.asos.com/ru/search/"
        self._search_item = search_item
        # Asos блокирует фейковые user-agent, поэтому пришлось вставить свой
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
        self._cout_items_on_page = 72

    def _to_count_items(self, parsed):
        """
        Подсчитывает количество найденных предметов
        :param parsed: готовая часть HTML
        :return: число типа int
        """
        try:
            items = super()._get_nums(parsed.find("p", {"data-auto-id": "styleCount", "class": "_2JQRAAs styleCount"}).text)
            res = int(items[0])
        except:
            res = 0
        return res

    def _correct_value_price(self, string):
        """
        Находит корректное значение цены товара
        :param string: Название товара, из которого нужно вытащить стоимость товара
        :return: Цену товара типа int
        """
        # товар может быть со скидкой и без
        # если товар без скидки, то будет поиск "Цена"
        # иначе - "текущая цена"
        index = string.index('текущая цена') if string.find('Цена') == -1 else string.index('Цена')
        try:
            price = string[index:]  # отбросить название товара, оставить информацию о цене
            price = price.replace(" ", "")  # убрать пробелы, чтобы корректно сработала функция по поиску цены в строке
            price = self._get_nums(price)  # найти из строки цену
            return int("".join(price[0]))
        except:
            assert "Can't get correct value"

    def _get_links_prices(self, pages):
        """
        Собирает ссылки на товары и цены товары
        :param pages: Количество страниц
        :return: Кортеж из ссылок и цен
        """
        links = []
        prices = []
        for page in range(1, pages + 1):
            time.sleep(0.1)
            params = {'page': page, 'q': self._search_item}
            responce = super()._get_responce(self._url, params, {"user-agent": self._user_agent})
            soup = super()._parse_html(responce.text)
            items = soup.find_all("article", {"data-auto-id": "productTile", "class": "_2qG85dG"})
            if len(items) == 0:
                assert "Wrong items tags"
            for obj in items:
                link = obj.find("a", class_="_3TqU78D").get("href")
                if link == None:
                    assert "Link not found. Need to find new tags."
                links.append(link)

                name = obj.find("a", class_="_3TqU78D").get("aria-label")
                if name == None:
                    assert "Name not found. Need to find new tags."
                price = self._correct_value_price(name)
                prices.append(price)
            print(f"сайт Asos.com, страница {page}/{pages} успешно обработана")
        if len(prices) == len(links):
            return links, prices
        else:
            assert "Count of links and prices is not equal"

    def to_go(self):
        """
        Запускает все функции, парсит цены и ссылки
        :return: Отсортированный по убыванию список кортежей типа "ссылка на товар - его цена", если неудачно - None
        """
        res = super()._get_responce(self._url, {"q": self._search_item}, {"user-agent": self._user_agent})
        soup = super()._parse_html(res.text)

        count_items = self._to_count_items(soup)
        if count_items == 0:
            return ()
        count_pages = super()._to_count_pages(count_items, self._cout_items_on_page)
        links, prices = self._get_links_prices(count_pages)
        objs = super()._to_zip(links, prices)
        objs.sort(key=lambda x: x[1], reverse=True)
        return objs


class Lamoda(Site):
    """
    Сайт lamoda.ru
    Имеет один открый метод to_go(), который выполняет все закрытые методы класса
    """

    def __init__(self, search_item):
        self._url = "https://www.lamoda.ru/catalogsearch/result/"
        self._search_item = search_item.replace(" ", "%20")
        self._user_agent = UserAgent().random
        self._cout_items_on_page = 60

    def _to_count_items(self, parsed):
        try:
            items = parsed.find("span", class_="products-catalog__head-counter").text
            res = int(super()._get_nums(items)[0])
        except:
            res = 0
        return res

    def _correct_value_price(self, html):
        """
        Находит корректное значение цены товара
        :param html: Название товара, из которого нужно вытащить стоимость товара
        :return: Цену товара типа int
        """
        try:
            prices = list()
            for tag in html:
                for ch in tag:
                    price = ch.replace(" ", "")
                    try:
                        price = int(price)
                    except:
                        continue
                    prices.append(price)
            return min(prices)
        except:
            assert "Can't get correct value"

    def _get_links_prices(self, pages):
        """
        Парсинг ссылок на товары и их цен
        :param html: страница с html, где находится нужная информация
        :return: кортеж из ссылок и цен (links, prices)
        """
        links = []
        prices = []
        for num in range(1, pages + 1):
            time.sleep(0.1)
            params = {"q": self._search_item,
                      "submit": "y",
                      "page": num}
            responce = super()._get_responce(self._url, params, {"user-agent": UserAgent().random})
            soup = super()._parse_html(responce.text)
            items = soup.find_all("div", class_="products-list-item")
            if len(items) == 0:
                assert "Wrong items tags"
            for item in items:
                link = item.find("a", class_="products-list-item__link link").get("href")
                if link == None:
                    assert "Link not found. Need to find new tags."
                link = "https://www.lamoda.ru" + link
                links.append(link)

                price = item.find("span", class_="price")
                if price == None:
                    assert "Name not found. Need to find new tags."
                price = self._correct_value_price(price)
                prices.append(price)
            print(f"сайт Lamoda.ru, страница {num}/{pages} успешно обработана")
        if len(prices) == len(links):
            return links, prices
        else:
            assert "Count of links and prices is not equal"

    def _to_zip(self, links, prices):
        """
        Делает соответствующую пару типа "ссылка на товар - его цена"
        :return: Кортежи пар типа "ссылка на товар - его цена"
        """
        pairs = []
        for i in range(len(links)):
            pairs.append(((links[i], prices[i])))
        return pairs

    def to_go(self):
        res = super()._get_responce(self._url, {"q": self._search_item, "submit": "y"},
                                    {"user-agent": self._user_agent})
        soup = super()._parse_html(res.text)
        count_items = self._to_count_items(soup)
        if count_items == 0:
            return ()
        count_pages = super()._to_count_pages(count_items, self._cout_items_on_page)
        links, prices = self._get_links_prices(count_pages)
        objs = super()._to_zip(links, prices)
        objs.sort(key=lambda x: x[1], reverse=True)
        return objs

def main():
    """
    Основная функция
    """
    while True:
        print("\nНапишите поисковый запрос (пример: vans кеды) или 'stop', чтобы выйти:")
        item = input()
        if item == "stop": break
        lamoda = Lamoda(item).to_go()
        asos = Asos(item).to_go()
        result = lamoda + asos
        if result == ():
            print("По вашему запросу ничего не найдено, попробуйте еще раз")
            continue
        result.sort(key=lambda x: x[1], reverse=True)
        for item in result:
            print(f"Price: {item[1]}, Link: {item[0]}")


if __name__ == '__main__':
    main()
