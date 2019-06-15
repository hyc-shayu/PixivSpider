# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
import os
import time


class ScrapypixivPipeline(object):
    def open_spider(self, spider):
        self.startTime = time.time()
        print('open pipelines')

    def process_item(self, item, spider):
        self.saveImg(item)
        return

    def saveImg(self, item):
        filePath = item['imagePath']
        if not os.path.exists(filePath):
            with open(filePath, 'wb') as f:
                f.write(item['imageContent'].body)
                print(f'保存 {filePath} 成功！')
        else:
            print(f'{filePath} is existed!')
        del item

    def close_spider(self, spider):
        print(f'close spider! speding {time.time()-self.startTime} s!')


class DownloadImgPipeline(ImagesPipeline):
    def open_spider(self, spider):
        super().open_spider(spider)
        self.startTime = time.time()
        print('open pipelines')

    def get_media_requests(self, item, info):
        if not hasattr(self, 'cookies'):
            self.cookies = info.spider.cookies
        for url in item['image_urls']:
            print(f'request for {url}')
            yield Request(url, headers={'Referer': item['referer']}, cookies=self.cookies)

    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def close_spider(self, spider):
        print(f'close spider! speding {time.time()-self.startTime} s!')
