# -*- coding: utf-8 -*-
import scrapy
from scrapyD.scrapyDouban.items import ScrapydoubanItem

class DoubanSpiderSpider(scrapy.Spider):
    # 爬虫的名字
    name = 'douban_spider'
    # 爬虫允许抓取的域名
    allowed_domains = ['movie.douban.com']
    # 爬虫抓取数据地址，给调度器
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        # xml的解析方法xpath
        movie_list = response.xpath("//div[@class='article']//ol[@class='grid_view']/li")
        # 解析当前页面的信息
        for i_item in movie_list:
            douban_item = ScrapydoubanItem()
            douban_item['serial_number'] = i_item.xpath(".//div[@class='item']//em/text()").extract_first()
            douban_item['movie_name'] = i_item.xpath(
                ".//div[@class='info']/div[@class='hd']/a/span[1]/text()").extract_first()
            descs = i_item.xpath(".//div[@class='info']//div[@class='hd']/p[1]/text()").extract()
            for i_desc in descs:
                i_desc_str = "".join(i_desc.split())
                douban_item['introduce'] = i_desc_str

            douban_item['star'] = i_item.xpath(".//span[@class='rating_num']/text()").extract_first()
            douban_item['evaluate'] = i_item.xpath(".//div[@class='star']//span[4]/text()").extract_first()
            douban_item['describle'] = i_item.xpath(".//p[@class='quote']/span/text()").extract_first()
            # print(douban_item)
            # 将返回结果压入item Pipline进行处理
            yield douban_item
        '''
        解释:
            1 每次for循环结束后,需要获取next页面链接:next_link
            2 如果到最后一页时没有下一页,需要判断一下
            3 下一页地址拼接: 点击第二页时页面地址是https://movie.douban.com/top250?start=25&filter= 恰好就是https://movie.douban.com/top250 和 <a href ...</a>中href的拼接
            4 callback=self.parse : 请求回调
        '''
        # 解析下一页
        next_link = response.xpath("//span[@class='next']/link/@href").extract()
        if next_link:
            next_link = next_link[0]
            yield scrapy.Request("https://movie.douban.com/top250" + next_link, callback=self.parse)


