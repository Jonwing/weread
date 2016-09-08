#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import random
import time
import requests


class ContentGenerator(object):
    def __init__(self, source=None):
        self.source = source

    def content(self, skip_lines=3, min_length=32, length=192):
        loop = 0
        with open(self.source, 'r') as f:
            for line in f:
                loop += 1
                if loop % skip_lines != 0:
                    continue
                l = len(line)
                if l < min_length:
                    continue
                if l > length:
                    content = line.decode('utf-8')
                    yield content[:length]


class WeRead(object):
    _default_header = {
        'Host': 'i.weread.qq.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    _base_api_url = 'https://i.weread.qq.com/'

    def __init__(self, user_header, content_source, **kwargs):
        self.client = requests
        self.book = ContentGenerator(content_source).content()
        self._header = self._default_header.copy()
        self._header.update(user_header)

    def review_list(self, params=None):
        print "reviewing"
        api_postfix = 'review/list'
        args = {
            'listType': 5,
            'bookId': 0,
            'synckey': 0,
            'private': 1
        }
        if params is not None:
            args.update(params)
        response = self.client.get(
            ''.join([self._base_api_url, api_postfix]),
            params=args,
            headers=self._header
        )
        self.handle_response(response)

    def read_book(self, data=None):
        print "reading book"
        if data is None:
            return
        try:
            summary = self.book.next()
        except StopIteration:
            return
        data.update({'summary': summary})
        api_postfix = 'book/read'
        header = self._header.copy()
        header.update({'Content-Type': 'application/json; charset=UTF-8'})
        url = ''.join([self._base_api_url, api_postfix])
        response = self.client.post(url, json=data, headers=header)
        self.handle_response(response)

    def set_app_online_time(self, ontime=2):
        print "setting online time"
        api_postfix = 'app/onlinetime'
        data = {'time': ontime}
        header = self._header.copy()
        header.update({'Content-Type': 'application/json; charset=UTF-8'})
        url = ''.join([self._base_api_url, api_postfix])
        response = self.client.post(url, json=data, headers=header)
        self.handle_response(response)

    def handle_response(self, res):
        try:
            print res.json()
        except (AttributeError, ValueError):
            print "response is not json formatted. status code: ", res.status_code


if __name__ == '__main__':
    header = {
        'accessToken': '',
        'vid': '',
        'osver': '',
        'appver': '',
        'basever': '',
        'beta': '0',
        'channelId': '',
        'User-Agent': '',
    }
    wr = WeRead(user_header=header, content_source='')
    repeat = 33
    read_book_data = {
        "appId": "",
        "bookId": "",
        "bookVersion": 0,
        "chapterOffset": 0,
        "chapterUid": 9,
        "progress": 33,
        # "readingTime": 186,
        # "summary": None
    }
    while repeat < 100:
        read_book_data['progress'] = read_book_data['progress'] + 1
        if repeat % 5 == 0:
            read_book_data["chapterUid"] = read_book_data["chapterUid"] + 1
        read_book_data['readingTime'] = 120 + random.choice([i for i in range(20)])
        wr.set_app_online_time(2)
        time.sleep(1)
        wr.read_book(read_book_data)
        time.sleep(1)
        wr.review_list()
        time.sleep(120)
        repeat += 1
