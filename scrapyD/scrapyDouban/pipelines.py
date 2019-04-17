# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
import csv
class ScrapydoubanPipeline(object):
    # 数据保存进json
    # def __init__(self):
    #     self.file = codecs.open('data.json',mode='wb',encoding='utf-8' )
    # def process_item(self, item, spider):
    #     line = json.dumps(dict(item), ensure_ascii = False) + "\n"
    #     self.file.write(line)
    #     return item
    # 数据保存进csv
    def __init__(self):
        self.file = codecs.open('data.csv','a+',encoding='utf-8' )
    def process_item(self, item, spider):
        writer = csv.writer(self.file)
        writer.writerow((item['serial_number'], item['movie_name'],item['evaluate'],item['describle'],
                         item['star']))
        return item
