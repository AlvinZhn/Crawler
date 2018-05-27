# -*- coding: utf-8 -*-
"""
@Author: 'Zhang'
"""

from pymongo.errors import DuplicateKeyError
from pyquery import PyQuery

from models import Crawler


class Gongyu(Crawler.Crawler):
    @classmethod
    def default_names(cls):
        names = super().default_names()
        names = names + [
            ('title', str, ''),
            ('location', str, ''),
            ('lng', float, 0),
            ('lat', float, 0),
            ('rent_type', str, ''),
            ('price', int, ''),
            ('room_type', str, ''),
            ('size', str, ''),
            ('url', str, ''),
        ]
        return names

    @staticmethod
    def default_filename(url):
        # http://hz.58.com/pinpaigongyu/pn/1/?minprice=800_2500
        # http://{city}.58.com/pinpaigongyu/pn/{page}/?minprice={min-price}_{max-price}
        city = url.split('//')[1].split('.')[0]
        page = url.split('pn/')[1].split('/', 1)[0]
        filename = '{}_{}_{}.html'.format(Crawler.Crawler.now().split(':')[0], city, page)
        return filename

    @classmethod
    def get_geoLocation(cls):
        infos = cls.find_all(lng='')
        for item in cls.all_json(infos):
            url = item.get('url')
            is_not_pass = True
            while (is_not_pass):
                try:
                    page = cls.load_from_url(url, cached=False)
                    content = page.decode()
                    x = content.split('____json4fe.lon')[1].split()[1].split("'")[1]
                    y = content.split('____json4fe.lon')[1].split()[4].split("'")[1]
                    cls.update(id=item.get('id'), form={'lng': x, 'lat': y})
                    is_not_pass = False
                except:
                    is_not_pass = True
                    print('failed')

    @classmethod
    def _info_from_page(cls, page):
        elements = PyQuery(page)
        main_url = elements('.newaplogo').attr('href')
        items = elements('.list').find("li")
        response = dict(
            end=False,
            data=[],
        )
        items_num = len(items)
        print('this page has [{}] data'.format(items_num))
        if items_num > 0:
            counter = 0
            for tag in items:
                section = PyQuery(tag)
                title = section('h2').text()
                sub_title = section('.room').text().split()
                price_tag = section('.money span b').text()
                try:
                    price = price_tag.split('-')[0]
                except:
                    price = price_tag
                form = dict(
                    title=title,
                    location=title.split(' ')[1],
                    rent_type=title.split('】')[0].split('【')[1],
                    price=price,
                    room_type=sub_title[0],
                    size=sub_title[1],
                    url=main_url[:-1] + section('a').attr('href').split('?', 1)[0],
                )
                try:
                    info = cls.new(form)
                except DuplicateKeyError as e:
                    counter += 1
                    print('Error: {},\n{} duplicated in this page'.format(e, counter))
                    if counter == items_num:
                        response['end'] = True
                        return response
                    else:
                        continue
                else:
                    response['data'].append(info)
        else:
            response['end'] = True
        return response

    @classmethod
    def _info_from_url(cls, url):
        filename = cls.default_filename(url)
        page = cls.load_from_url(url, filename=filename)
        response = cls._info_from_page(page)
        return response

    @classmethod
    def update_data(cls):
        # http://{city}.58.com/pinpaigongyu/pn/{page}/?minprice={min-price}_{max-price}
        page = 1
        end = False
        data_list = []
        while not end:
            print('getting data from page [{}], end is [{}]'.format(page, end))
            url = 'http://hz.58.com/pinpaigongyu/pn/{}/?minprice=800_2800'.format(page)
            response = cls._info_from_url(url)
            end = response['end']
            data_list += response['data']
            page += 1
            print('working on response from page [{}], end is [{}]'.format(page, end))
        time_now = cls.now()
        form = {'last_checked_time': time_now}
        if (len(data_list)) > 0:
            form.update({'updated_time': time_now})
        Crawler.Crawler.update(
            query={'site': cls.__name__},
            form=form,
        )
        # cls.get_geoLocation()
        return cls.all_json(data_list)
