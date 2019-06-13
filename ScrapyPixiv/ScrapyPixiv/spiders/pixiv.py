# -*- coding: utf-8 -*-
import scrapy
from .mySetting import *
from scrapy.http.cookies import CookieJar
import re
from scrapy.http import Request, Response, FormRequest
import os
from datetime import date
from ..items import ScrapypixivItem
import json


class PixivSpider(scrapy.Spider):
    name = 'pixiv'
    # allowed_domains = []
    # start_urls = ['https://www.pixiv.net/']
    custom_settings = {
        'LOG_LEVEL': 'ERROR'
    }
    startUrl = LOGIN_PAGE_URL
    loginAPI = LOGIN_API
    savePath = None

    _discorveryUrl = DISCOVERY_URL
    _discorveryReferer = 'https://www.pixiv.net/discovery'
    _pidBaseUrl = PID_BASE_URL
    _ajaxRequest = AJAX_BASE_REQUEST

    count = 0
    cookies = {}

    def start_requests(self):
        p = int(input('爬取的插画数量:'))
        self._discorveryUrl = DISCOVERY_URL % p
        return [Request(self.startUrl, callback=self.login)]

    # after login save cookies, then request
    # in future, I will set maxSizePid
    def saveCookies(self, response):
        dateTime = str(date.today())
        self.savePath = os.path.join(SAVE_PATH, dateTime)
        if not os.path.isdir(self.savePath):
            os.makedirs(self.savePath)
        cookieJar = CookieJar()
        cookieJar.extract_cookies(response, response.request)
        for cookie in cookieJar:
            self.cookies[cookie.name] = cookie.value
        print('Log in completed!')
        yield Request(self._discorveryUrl, headers={'Referer': self._discorveryReferer}, cookies=self.cookies, callback=self.parse)

    def parse(self, response):
        rawDict = eval(response.text)
        pidLst = rawDict['recommendations']
        for pid in pidLst:
            Referer = f'{self._pidBaseUrl}{pid}'
            yield Request(self._ajaxRequest % pid, headers={'Referer': Referer}, cookies=self.cookies, callback=self.director)

    def director(self, response):
        for request in self.requestOriginalImages(self.getOriginalUrlList(response), response.request.headers.get('Referer')):
            yield request

    # getting image original url according to pixiv json regular
    def getOriginalUrlList(self, response):
        urlJSON = json.loads(response.text)['body']
        originalUrlList = [url['urls']['original'] for url in urlJSON]
        return originalUrlList

    def requestOriginalImages(self, urlList, referer):
        for url in urlList:
            yield Request(url, headers={'Referer': referer}, cookies=self.cookies, callback=self.saveItem)

    def saveItem(self, response):
        item = ScrapypixivItem()
        item['imagePath'] = os.path.join(self.savePath, response.url.split('/')[-1])
        item['imageContent'] = response
        return item

    @staticmethod
    def __getPostKey(loginHtml):
        pattern = re.compile('<input type="hidden".*?value="(.*?)">')
        result = re.search(pattern, loginHtml)
        return result.group(1)

    def login(self, response):
        print('Logging in...')
        postKey = self.__getPostKey(response.text)
        loginData = {
            'pixiv_id': PIXIV_ID,
            'password': PASSWORD,
            'post_key': postKey,
            'return_to': RETURN_TO
        }
        return FormRequest(self.loginAPI, formdata=loginData, callback=self.saveCookies)
