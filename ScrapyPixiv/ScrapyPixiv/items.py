# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class ScrapypixivItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    imagePath = Field()
    imageContent = Field()


class ImageItem(Item):
    image_urls = Field()
    referer = Field()
    images = Field()
