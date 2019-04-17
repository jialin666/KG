# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapydoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 序列号
    serial_number = scrapy.Field()
    # 电影名
    movie_name = scrapy.Field()
    # 电影简介
    introduce = scrapy.Field()
    # 评分
    star = scrapy.Field()
    # 评价信息
    evaluate = scrapy.Field()
    # 详细信息
    describle = scrapy.Field()


    pass
