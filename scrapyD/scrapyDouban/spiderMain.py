#!/usr/bin/env python
# encoding: utf-8
'''
@author: mengmeng-guo
@project: KG
@file: spiderMain.py
@time: 2019/4/16 14:51
@desc:
'''

from  scrapy import cmdline
# 输出未过滤的页面信息
cmdline.execute('scrapy crawl douban_spider'.split())