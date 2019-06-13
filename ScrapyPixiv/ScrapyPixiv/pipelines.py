# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
import os


class ScrapypixivPipeline(object):
    def open_spider(self, spider):
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
        print('close spider!')


class DownloadImgPipeline(ImagesPipeline):
    pass
