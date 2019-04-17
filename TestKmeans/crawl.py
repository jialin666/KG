#!/usr/bin/env python
# encoding: utf-8
'''
@author: mengmeng-guo
@project: KG
@file: crawl.py
@time: 2019/4/17 16:37
@desc:
'''
import re
import multiprocessing
from selenium import webdriver
import time
from  bs4 import BeautifulSoup
import requests

#将结果写入'articles.csv'
fw=open('articles.csv','a',encoding='utf8')
#请求头
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
}

#获取常用3000汉字
hanzi=get_commmon_hanzi()#"啊阿埃挨哎唉哀皑癌蔼矮艾碍爱隘鞍氨安俺......"


#解析详情页
def parse_page(url,tag):
    res=requests.get(url,headers=headers)
    try:
        # 去除停用词
        text=re.findall(r'content:(.*\;\'\,)?',res.text,re.S)[0]
    except:
        print(url,tag,res.headers)
        return
    result=list()
    #只保留常用汉字，去掉标点符号和其他特殊字符
    for c in text:
        if c in hanzi:
            result.append(c)
    fw.write('{},{}\n'.format(tag,''.join(result)))


#获取文章的url，因为没能破解_signature，所以使用selenium
def crawl_news(driver, url):
    driver = webdriver.PhantomJS(executable_path='utils/phantomjs.exe')
    tag=url.split('/')[-2]
    driver.implicitly_wait(5)  # seconds
    driver.get(url)
    time.sleep(5)
    #拖动滚动条100次
    for _ in range(100):
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, 'lxml')
    items = soup.select('.wcommonFeed ul .item')
    # print(len(items))
    results=list()
    for item in items:
        try:
            href = item.find('a', class_='link title')['href']
            if href.find('/group/') != -1:
                results.append(['https://www.toutiao.com{}'.format(href),tag])
        except:
            pass
    driver.close()
    return results


def crawl_begin():
    #“科技”和“娱乐”
    news_url=['https://www.toutiao.com/ch/news_tech/','https://www.toutiao.com/ch/news_entertainment/']
    items=list()
    for url in news_url:
        items.extend(crawl_news(url=url))
    print(len(items))
    #打乱items的顺序
    # random.shuffle(items)
    #使用进程池
    pool = multiprocessing.Pool(processes=4)
    for item in items:
        pool.apply_async(parse_page, (item[0],item[1]))
    pool.close()
    pool.join()  # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print("done.")


if __name__ == '__main__':
    crawl_begin()
