#!/usr/bin/env python
# encoding: utf-8
'''
@author: mengmeng-guo
@project: KG
@file: t.py
@time: 2019/4/12 17:01
@desc:
'''

'''
hanlp 调用textrank的demo
'''
from pyhanlp import *
def getAbstract():
    for term in HanLP.segment('下雨天地面积水'):
        print('{}\t{}'.format(term.word, term.nature)) # 获取单词与词性
    testCases = [
        "商品和服务",
        "结婚的和尚未结婚的确实在干扰分词啊",
        "买水果然后来世博园最后去世博会",
        "中国的首都是北京",
        "欢迎新老师生前来就餐",
        "工信处女干事每月经过下属科室都要亲口交代24口交换机等技术性器件的安装工作",
        "随着页游兴起到现在的页游繁盛，依赖于存档进行逻辑判断的设计减少了，但这块也不能完全忽略掉。"]
    for sentence in testCases: print(HanLP.segment(sentence))
    # 关键词提取
    document = "水利部水资源司司长陈明忠9月29日在国务院新闻办举行的新闻发布会上透露，" \
               "根据刚刚完成了水资源管理制度的考核，有部分省接近了红线的指标，" \
               "有部分省超过红线的指标。对一些超过红线的地方，陈明忠表示，对一些取用水项目进行区域的限批，" \
               "严格地进行水资源论证和取水许可的批准。"
    print(HanLP.extractKeyword(document, 2))
    # 自动摘要
    print(HanLP.extractSummary(document, 3))
    # 依存句法分析
    print(HanLP.parseDependency("徐先生还具体帮助他确定了把画雄鹰、松鼠和麻雀作为主攻目标。"))
class Docrank:
    def __init__(self,newsPath,storyPath,outPath):
        print("运行开始-----")
        self.newsPath =newsPath
        self.storyPath = storyPath
        self.outPath = outPath
    # 使用hanlp获取摘要
    def getSummary(self):
         #doc_dict的结构：{“文章名”：[摘要一，摘要二。。。]}}
        summaryDict = {}
        for root, dirs, files in os.walk(self.newsPath):
            for file in files:
                filepath = os.path.join(root, file)
                # 如果文件存在则打开
                if (os.path.exists(filepath)):
                     # print("filepath:", filepath)
                    document = open(filepath,encoding = "gbk").read()
                    onePageSummary = HanLP.extractSummary(document, 3)
                    print("onePageSummary",onePageSummary)
                    #打印分词后的信息：
                    # for each_list in word_list:
                    #     print(each_list)
                    summaryDict[file] = onePageSummary
                else:
                    print("不存在文件：",filepath)
        # 将词频信息输出到txt
        self.write_util(self.outPath,"summaryDict.txt",summaryDict)
        for key, value in summaryDict.items():
            print('{key}:{value}'.format(key=key, value=value))
        return summaryDict
def main():
    print('this message is from main function')
    # D:\Users\mengmeng-guo\PycharmProjects\KG\ImporEventExtractor
    curPath = os.getcwd()
    # D:\Users\mengmeng-guo\PycharmProjects\KG
    dirName = os.path.dirname(os.getcwd())
    event_list = ['视觉中国事件', '复联4','996事件']
    for event in event_list:
        # 爬取的新闻路径
        newsPath = os.path.join(os.path.join(dirName, 'EventM\EventMonitor\\news'), event)
        if not os.path.exists(newsPath):
            os.makedirs(newsPath)
        print("newsPath", newsPath)

        # 存储结果路径
        outPath = os.path.join(os.path.join(curPath, 'out'), event)
        print("outPath拼接", outPath)
        if not os.path.exists(outPath):
            os.makedirs(outPath)

        storyPath = os.path.join(os.path.join(curPath, 'st'), event)
        print("storyPath", storyPath)
        if not os.path.exists(storyPath):
            os.makedirs(storyPath)

        handler = Docrank(newsPath,storyPath,outPath)
        # doc_graph = handler.doc_graph()
        # timelines = handler.timeline(doc_graph)
        abstract = handler.getSummary()

if __name__ == '__main__':
    main()

