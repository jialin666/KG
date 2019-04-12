#!/usr/bin/env python
# encoding: utf-8
'''
@author: mengmeng-guo
@project: KG
@file: t.py
@time: 2019/4/12 17:01
@desc:
'''
import os
from os import path
# CUR = '/'.join(os.path.abspath(__file__).split('/')[:-2])
# news_path = os.path.join(CUR, 'new')
# print(news_path)
#
# print( '***获取当前目录***')
# print (os.getcwd())
# print (os.path.abspath(os.path.dirname(__file__)))
#
# print ('***获取上级目录***')
# print (os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
# print (os.path.abspath(os.path.dirname(os.getcwd())))
# print (os.path.abspath(os.path.join(os.getcwd(), "..")))
#
# print ('***获取上上级目录***')
# print(os.path.abspath(os.path.join(os.getcwd(), "../..")))

d = path.dirname(__file__)  #返回当前文件所在的目录
# 返回d所在目录规范的绝对路径
print(path.abspath(d))


curPath = os.getcwd()
# KG
dirName = os.path.dirname(os.getcwd())
eventName = '孟'
# EventM/EventMonitor/news
print("dirname:",curPath)

news_path = os.path.join(os.path.join(curPath,'out'),eventName)
print("拼接",news_path)

newspath = os.path.join(os.path.join(dirName,'EventM\EventMonitor\\news'),eventName)
print("拼接外部",newspath)

trainfile = 'KG/EventM/EventMonitor/news/孟晚舟事件'
storypath = 'story/孟晚舟事件'
graphpath = 'output/孟晚舟事件'
countwordpath = 'output/孟晚舟事件'
if not os.path.exists(newspath):
    os.makedirs(newspath)