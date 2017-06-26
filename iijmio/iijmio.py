# -*- coding:utf8 -*-
from errbot import BotPlugin, botcmd
from datetime import datetime
import requests
import bs4


class Iijmio(BotPlugin):
    """
    IIJmio monitor
    """

    def get_configuration_template(self):
        return {
            'username': "YOUR_IIJMIO_USERNAME",
            'password': "YOUR_IIJMIO_PASSWORD", }

    @botcmd(name='iijmio_fetch_daily')
    def fetch_currently_usage(self, message, args):
        if self.config is None:
            return "not config"
        if not self.config.get('username', None) \
                or not self.config.get('username', None):
            return "Example"
        client = IijmioSession(**self.config)
        result = client.fetch_usage()
        return result

    @botcmd(name='iijmio_remain')
    def fetch_remain(self, message, args):
        if self.config is None:
            return "not config"
        if not self.config.get('username', None) \
                or not self.config.get('username', None):
            return "Example"
        client = IijmioSession(**self.config)
        result = client.fetch_remain()
        if result == 0:
            return '今月のクーポン残量はありません'
        else:
            return '今月は残り{}MB利用可能です'.format(result)

class IijmioSession(object):
    URL_BASE = 'https://www.iijmio.jp'

    def __init__(self, username, password):
        self.session = requests.Session()
        self.username = username
        self.password = password

    def url(self, path):
        return self.URL_BASE + path

    def login(self):
        resp = self.session.get(self.url('/auth/login.jsp'))
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        params = {
            e.attrs['name']: e.attrs.get('value')
            for e in soup.find('form').findAll('input')}
        params['j_username'] = self.username
        params['j_password'] = self.password
        post_url  = self.url(soup.find('form').attrs['action'])
        resp = self.session.post(post_url, params)
        return self.session

    def fetch_daily_usage(self):
        session = self.login()
        resp = session.get(self.url('/service/setup/hdd/viewdata/'))
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        table = soup.find('table', 'base2')
        params = {
            e.attrs['name']: e.attrs.get('value')
            for e in table.find_all('input')}
        post_url = self.url(table.find('form').attrs['action'])
        resp = session.post(post_url, params)
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        rows = [tr for tr in soup.find('table', 'base2').find_all('tr')[3:]]
        records = {}
        for row in rows:
            cols = row.find_all('td')
            date_ = datetime.strptime(cols[0].text, '%Y年%m月%d日').date()
            records[date_] = {'high': int(cols[1].text.strip()[:-2]), 'low': int(cols[2].text.strip()[:-2])}
        return records

    def fetch_remain(self):
        session = self.login()
        resp = session.get(self.url('/service/setup/hdd/couponstatus/'))
        soup = bs4.BeautifulSoup(resp.content, 'html5lib')
        table = soup.find('table', 'base2')
        total_row = table.find_all('tr')[1]
        return int(total_row.find_all('td')[1].text.strip()[:-2])
