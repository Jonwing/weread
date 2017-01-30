#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
import random
import time
import requests


class ContentGenerator(object):
    '''
    class to generate summary
    :param source: the source path of content
    '''
    def __init__(self, source=None):
        self.source = source
        self._formula = ""

    def content(self, skip_lines=3, min_length=32, length=192):
        loop = 0
        with open(self.source, 'r') as f:
            for line in f:
                loop += 1
                if loop % skip_lines != 0:
                    continue
                if len(line) < min_length:
                    continue
                if len(line) > length:
                    content = line.decode('utf-8')
                    yield content[:length]

    def read_part(self, start_at=0, content_length=192):
        if start_at >= 100:
            raise ValueError("start_at should less than 100")
        with open(self.source, "r") as f:
            self._formula = f.read().decode("utf-8")
        formula_length = len(self._formula)
        start_position = start_at * formula_length / 100
        end_position = start_position + content_length
        while end_position < formula_length:
            partial = self._formula[start_position:end_position]
            progress = end_position * 100 / formula_length
            start_position = end_position
            end_position = start_position + content_length
            yield partial, progress


class WeRead(object):
    _default_header = {
        'Host': 'i.weread.qq.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    _base_api_url = 'https://i.weread.qq.com/'

    def __init__(self, user_header, content_source, **kwargs):
        self.client = requests
        self._header = self._default_header.copy()
        self._header.update(user_header)
        start_at = kwargs.get('start_at', 0)
        self.book = ContentGenerator(content_source).read_part(start_at=start_at)

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

    def read_book(self, data=None, read_time=10):
        print "reading book"
        if data is None:
            return

        # read for 10 minutes
        read_time_seconds = read_time * 60 / 10
        try:
            for x in range(read_time_seconds):
                self.summary, self._progress = self.book.next()
        except StopIteration:
            # reraise it
            raise
        data.update({'summary': self.summary, "progress": self._progress})
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
        'accessToken': '#token',
        'vid': '#vid',
        'osver': '#7.1.1',
        'appver': '#appversion',
        # 'basever': '',
        'beta': '0',
        'channelId': '4',
        'User-Agent': '#UserAgent'
    }
    read_book_data = {
        "appId": "",
        "bookId": "",
        "bookVersion": 10086,
        "chapterOffset": 1024,
        "chapterUid": 1,
        "progress": 1,
        # "readingTime": 186,
        # "summary": None
    }
    wr = WeRead(user_header=header, content_source='byx.txt', start_at=read_book_data['progress'])
    sleep_count = 0
    while True:

        read_book_data['progress'] = read_book_data['progress'] + 1
        if sleep_count % 15 == 0:
            read_book_data["chapterUid"] = read_book_data["chapterUid"] + 1
        read_book_data['readingTime'] = 600 + random.choice([i for i in range(20)])
        wr.set_app_online_time(2)
        time.sleep(1)
        if sleep_count % 5 == 0:
            try:
                wr.read_book(read_book_data)
                time.sleep(1)
            except StopIteration:
                print "Done, loop count: %s" % sleep_count
                break
        wr.review_list()
        sleep_count += 1
        time.sleep(120)
