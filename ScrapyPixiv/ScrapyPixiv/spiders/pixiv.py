# -*- coding: utf-8 -*-
import scrapy
from .mySetting import *
from scrapy.http.cookies import CookieJar
import re
from scrapy.http import Request, Response, FormRequest
import os
from ..items import ScrapypixivItem, ImageItem
import json
from datetime import date
try:
    from setting import *
except Exception as e:
    pass
from abc import abstractmethod


class myBasePixivSpider(scrapy.Spider):
    custom_settings = {
        'LOG_LEVEL': 'ERROR'
    }

    _discorveryUrl = DISCOVERY_URL
    _discorveryReferer = 'https://www.pixiv.net/discovery'
    _pidBaseUrl = PID_BASE_URL
    _ajaxRequest = AJAX_BASE_REQUEST

    startUrl = LOGIN_PAGE_URL
    loginAPI = LOGIN_API

    cookies = {}

    @staticmethod
    def __getPostKey(loginHtml):
        pattern = re.compile('<input type="hidden".*?value="(.*?)">')
        result = re.search(pattern, loginHtml)
        return result.group(1)

    def start_requests(self):
        p = int(input('爬取的插画数量:'))
        self._discorveryUrl = DISCOVERY_URL % p
        return [Request(self.startUrl, callback=self.login)]

    # after login save cookies, then request
    # in future, I will set maxSizePid
    def saveCookies(self, response):
        cookieJar = CookieJar()
        cookieJar.extract_cookies(response, response.request)
        for cookie in cookieJar:
            self.cookies[cookie.name] = cookie.value
        print('Log in completed!')
        return Request(self._discorveryUrl, headers={'Referer': self._discorveryReferer}, cookies=self.cookies, callback=self.parse)

    def parse(self, response):
        rawDict = eval(response.text)
        pidLst = rawDict['recommendations']
        for pid in pidLst:
            Referer = f'{self._pidBaseUrl}{pid}'
            yield Request(self._ajaxRequest % pid, headers={'Referer': Referer}, cookies=self.cookies, callback=self.director)

    @abstractmethod
    def director(self, response):
        pass

    @staticmethod
    @abstractmethod
    def requestOriginalImages(urlList, referer):
        pass

    # getting image original url according to pixiv json regular
    @staticmethod
    def getOriginalUrlList(response):
        urlJSON = json.loads(response.text)['body']
        originalUrlList = [url['urls']['original'] for url in urlJSON]
        return originalUrlList

    def login(self, response):
        print('Logging...')
        postKey = self.__getPostKey(response.text)
        loginData = {
            'pixiv_id': PIXIV_ID,
            'password': PASSWORD,
            'post_key': postKey,
            'return_to': RETURN_TO
        }
        return FormRequest(self.loginAPI, formdata=loginData, callback=self.saveCookies)


class PixivSpider1(myBasePixivSpider):
    name = 'pixiv1'
    savePath = None

    # after login save cookies, then request
    # in future, I will set maxSizePid
    def saveCookies(self, response):
        dateTime = str(date.today())
        self.savePath = os.path.join(SAVE_PATH, dateTime)
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)
        return super().saveCookies(response)

    def director(self, response):
        for request in self.requestOriginalImages(self.getOriginalUrlList(response),
                                                  response.request.headers.get('Referer')):
            yield request

    def requestOriginalImages(self, urlList, referer):
        for url in urlList:
            yield Request(url, headers={'Referer': referer}, cookies=self.cookies, callback=self.saveItem)

    def saveItem(self, response):
        item = ScrapypixivItem()
        item['imagePath'] = os.path.join(self.savePath, response.url.split('/')[-1])
        item['imageContent'] = response
        return item


class PixivSpider(myBasePixivSpider):
    name = 'pixiv2'

    def director(self, response):
        return self.requestOriginalImages(self.getOriginalUrlList(response), response.request.headers.get('Referer'))

    @staticmethod
    def requestOriginalImages(urlList, referer):
        # for url in urlList:
        #     yield Request(url, headers={'Referer': referer}, cookies=self.cookies, callback=self.saveItem)
        item = ImageItem()
        item['image_urls'] = urlList
        item['referer'] = referer
        return item
