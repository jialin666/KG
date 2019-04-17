#!/usr/bin/env python3
# coding: utf-8
# File: doc_rank.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-9
'''
项目流程：
1、爬取关键词新闻（EventMonitor）
2、jieba分词，词频统计，为每个文章维护一个词频字典 seg_files()
3、计算文章间的外链值（相似度）,维护文章间的链接图 doc_graph（）（依据文档排名算法DocRank，类似于textRank算法求摘要的过程，将每篇文章当做是一个句子）
4、重要度排序  使用textRank 的计算公式 计算PR值  textrank_graph.rank()
5、取同一个时间内的最要度最大的新闻作为重大事件的纪录 timeline（） 输出timeline.txt

'''

import jieba.posseg as pseg
from collections import Counter
from collections import defaultdict
import math
from pyhanlp import *
from EventM.EventMonitor import crawl

# 使用textRank 的就算公式 计算新闻文章的PR值
class textrank_graph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.d = 0.85 #d是阻尼系数，一般设置为0.85
        self.min_diff = 1e-5 #设定收敛阈值

    #添加节点之间的边
    def addEdge(self, start, end, weight):
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    #节点排序。依据pageRank的计算公式计算各个新闻的PR值，即重要度
    def rank(self):
        #默认初始化权重
        weight_deault = 1.0 / (len(self.graph) or 1.0)
        #nodeweight_dict, 存储节点的权重
        nodeweight_dict = defaultdict(float)
        #outsum，存储节点的出度权重
        outsum_node_dict = defaultdict(float)
        #根据图中的边，更新节点权重
        for node, out_edge in self.graph.items():
            #是 [('是', '全国', 1), ('是', '调查', 1), ('是', '失业率', 1), ('是', '城镇', 1)]
            nodeweight_dict[node] = weight_deault
            # 将该页面出度的链接权重相加
            outsum_node_dict[node] = sum((edge[2] for edge in out_edge), 0.0)
        #初始状态下的textrank重要性权重
        sorted_keys = sorted(self.graph.keys())
        # print("nodeweight_dict:", nodeweight_dict)
        # print("outsum_node_dict:", outsum_node_dict)  {'2002-03-20@纪念亡故阿嬷 立委助理捐结婚礼金防酒驾 - 生活 - 中时': 156.0,
        #设定迭代次数，
        step_dict = [0]
        for step in range(1, 1000):
            for node in sorted_keys:
                s = 0
                #计算公式：(edge_weight/outsum_node_dict[edge_node])*node_weight[edge_node]
                for e in self.graph[node]:
                    # PR=l()*PR
                    s += e[2] / outsum_node_dict[e[1]] * nodeweight_dict[e[1]]
                #     e[2] / outsum_node_dict[e[1]]  相当于归一化  nodeweight_dict[e[1]]相当于1/N
                #计算公式：(1-d) + d*s
                #textRank 的计算公式
                nodeweight_dict[node] = (1 - self.d) + self.d * s
            step_dict.append(sum(nodeweight_dict.values()))
            # print("sum(nodeweight_dict.values()):",sum(nodeweight_dict.values()))
            # print("step_dict:",step_dict)

            if abs(step_dict[step] - step_dict[step - 1]) <= self.min_diff:
                break

        #利用Z-score进行权重归一化，也称为离差标准化，是对原始数据的线性变换，使结果值映射到[0 - 1]之间。
        #先设定最大值与最小值均为系统存储的最大值和最小值
        (min_rank, max_rank) = (sys.float_info[0], sys.float_info[3])
        for w in nodeweight_dict.values():
            if w < min_rank:
                min_rank = w
            if w > max_rank:
                max_rank = w

        for n, w in nodeweight_dict.items():
            nodeweight_dict[n] = (w - min_rank/10.0) / (max_rank - min_rank/10.0)

        return nodeweight_dict



class Docrank:
    def __init__(self,newsPath,storyPath,outPath):
        print("1 运行开始")
        self.newsPath =newsPath
        self.storyPath = storyPath
        self.outPath = outPath

        # self.trainfile = 'KG/EventM/EventMonitor/news/孟晚舟事件'
        # self.storypath = 'story/孟晚舟事件'
        # self.graphpath = 'output/孟晚舟事件'
        # self.countwordpath = 'output/孟晚舟事件'
        # 调用方法，为每篇文章维护一个词频字典
        self.doc_dict = self.seg_files()

    '''对训练文本进行分词等处理，并为每篇文章维护一个词频字典'''
    def seg_files(self):
        print("2 每篇文章维护一个词频字典")
        #doc_dict的结构：{“文章名”：{单词1：词频；单词2：词频。。。}}
        doc_dict = {}
        for root, dirs, files in os.walk(self.newsPath):
            for file in files:
                filepath = os.path.join(root, file)
                # 如果文件存在则打开
                if (os.path.exists(filepath)):
                    # print("filepath:", filepath)
                    word_list = [w.word for w in pseg.cut(open(filepath,encoding = "gbk").read()) if w.flag[0] not in ['x', 'w', 'u', 'c', 'p', 'q', 't', 'f', 'd'] and len(w.word) > 1]
                    word_dict = {i[0]: i[1] for i in Counter(word_list).most_common() if i[1] > 1}
                    #打印分词后的信息：
                    # for each_list in word_list:
                    #     print(each_list)
                    doc_dict[file] = word_dict
                else:
                    print("不存在文件：",filepath)
        # 将词频信息输出到txt
        self.write_util(self.outPath,"countWord.txt",doc_dict)
        # for key, value in doc_dict.items():
        #     print('{key}:{value}'.format(key=key, value=value))
        return doc_dict

    # 使用hanlp获取摘要
    def getSummary(self):
        # doc_dict的结构：{“文章名”：[摘要一，摘要二。。。]}}
        summaryDict = {}
        onePageDict = {}
        for root, dirs, files in os.walk(self.newsPath):
            for file in files:
                filepath = os.path.join(root, file)
                # 如果文件存在则打开
                if (os.path.exists(filepath)):
                    # print("filepath:", filepath)
                    document = open(filepath, encoding="gbk").read()
                    onePageSummary = HanLP.extractSummary(document, 3)
                    # print("onePageSummary", onePageSummary)
                    # 打印分词后的信息：
                    # for each_list in word_list:
                    #     print(each_list)
                    onePageDict [file] = onePageSummary
                    summaryDict[file] = onePageDict
                else:
                    print("不存在文件：", filepath)
        # 将词频信息输出到txt
        self.write_util(self.outPath, "summaryDict.txt", summaryDict)

        return summaryDict

    '''为文章维护一个textrank表'''
    def doc_graph(self):
        print("3 为文章维护一个textrank表")
        #实例化textrank_graph 类,主要包含文章节点之间的边和权重，迭代计算后可以找出重要的文章
        g = textrank_graph()
        cm = defaultdict(int)
        for doc1, word_dict1 in self.doc_dict.items():
            for doc2, word_dict2 in self.doc_dict.items():
                #print("doc1:"+doc1+"doc2:"+doc2)
                if doc1 == doc2:
                    #同一篇文章时不进行计算，直接跳过
                    continue
                #print("word_dict1:",word_dict1)
                #print("word_dict2:",word_dict2)  一篇文章的词频统计输出示例：{'关系': 13, '双方': 12, '中国': 11, '合作': 11, }
                # 调用计算文章之间的外链值
                score = self.calculate_weight(word_dict1, word_dict2)
                pair = tuple((doc1, doc2))
                #print("score",score)
                #print("pair:",pair[:])
                if score > 0:
                    cm[(pair)] = score
        # print("添加文章图谱的节点函数")
        for terms, w in cm.items():
            #添加节点函数
            # print("terms0:",terms[0])
            # print("terms1:",terms[1])
            # print("w:",w)
            g.addEdge(terms[0], terms[1], w)

        # 打印数据类型：{文章一：[（文章一，文章2，score)，。。。]},将会构造一个对称的链接矩阵
        # print("g:",g.graph)
        # 将由文章间的外链值构成的图输出到txt
        self.write_util(self.outPath,"textGraph.txt",g.graph)
        print('4 调用文章图谱的节点排序函数，计算文章的重要度PR值')
        nodes_rank = g.rank()
        # 根据重要度降序排
        nodes_rank = sorted(nodes_rank.items(), key=lambda asd:asd[1], reverse=True)
        # print("after rank:\n", nodes_rank[:5])
        # {'2018-12-06@【掘金冲锋号】孟晚舟被捕事件最新消息': 0.07705318030986552, '2018-12-06@华为回应孟晚舟事件':0.2}

        #正常的textRank方法在排序后会生成topK个关键词

        return nodes_rank[:]

    '''辅助函数——计算文章之间的相关性'''
    def calculate_weight(self, word_dict1, word_dict2):
        score = 0
        #set.intersection(set1, set2 ... etc)  ,返回多个集合的交集
        interwords = set(list(word_dict1.keys())).intersection(set(list(word_dict2.keys())))
        for word in interwords:
            score += round(math.tanh(word_dict1.get(word)/word_dict2.get(word)))
        return score

    '''将同一时间的文章取重要度最高的文章若其PR值》0.4则加入重要新闻列表中'''
    def timeline(self, nodes_rank):
        # 时间线新闻纪录，即同一个时间只挑选重要度最高的新闻
        # 将最后的重要事件输出
        f_timelines = open(os.path.join(self.outPath,'timelines.txt'), 'w+',encoding='utf-8')
        # 将所有事件按照重要度排序后输出
        f_important = open(os.path.join(self.outPath,'important_doc.txt'), 'w+',encoding='utf-8')
        date_dict = {}
        timelines = {}
        print("5 将同一时间的文章按照重要性进行排序")
        for item in nodes_rank:
            f_important.write(item[0] + ' ' + str(item[1]) + '\n')
            doc = item[0]
            # 取出时间
            date = int(item[0].split('@')[0].split(' ')[0].replace('-',''))
            #date = int(item[0].split('@')[0].split(' ')[0])
            #print("date:\n", date)
            if date not in date_dict:
                date_dict[date] = {}
                date_dict[date][doc] = item[1]
            else:
                date_dict[date][doc] = item[1]
        print("向story文件夹写入数据,每一个时间文件下存放该时间的新闻----")
        # print("date_dict:",date_dict)  date_dict: {20190225: {'2019-02-25@好看能打！小米9详细评测：全面进化的骁龙855旗舰标杆': 1.0, '2019-02-25@小米9和小米9se摄像头区别': 0.32799423968674074
        for date, doc_dict in date_dict.items():
            f = open(os.path.join(self.storyPath, str(date)), 'w+',encoding='utf-8')
            #同一个时间点，所有文章按重要性倒序排
            doc_dict = sorted(doc_dict.items(), key = lambda asd:asd[1], reverse=True)
            # print("doc_dict:",doc_dict) 输出：doc_dict: [('2019-02-25@好看能打！小米9详细评测：全面进化的骁龙855旗舰标杆', 1.0), ('2019-02-25@小米9和小米9se摄像头区别', 0.32799423968674074)
            # 当同一时间的重要性最大的文章的权重大于0.4时，则将该新闻放进重大新闻时间线中
            if doc_dict[0][1] > 0.4 :
                timelines[date] = [str(doc_dict[0][0]), str(doc_dict[0][1])]
            for i in doc_dict:
                f.write(i[0] + "\t" + str(i[1]) + '\n')
            f.close()
        print("向timelines写入数据")
        for i in sorted(timelines.items(), key=lambda asd:asd[0], reverse=False):
            f_timelines.write(str(i[0]) + ' ' + ' '.join(i[1]) + '\n')

        f_timelines.close()
        f_important.close()
        print("6 运行结束")
        return timelines
    # 辅助函数，将中间形成的数据输出在txt中
    def write_util(self,filepath,text_name,dict):
         # 创建文件并写入
         w_text_graph = open(os.path.join(filepath, text_name), 'w+',encoding='utf-8')
         # js = json.dumps(dict)  转成json后乱码
         w_text_graph.write(str(dict))
         # for temp in dict.items():
         #     w_text_graph.write(temp+'\n')

         w_text_graph.close()

def main():
    print('this message is from main function')
    # D:\Users\mengmeng-guo\PycharmProjects\KG\ImporEventExtractor
    curPath = os.getcwd()
    # D:\Users\mengmeng-guo\PycharmProjects\KG
    dirName = os.path.dirname(os.getcwd())
    event_list = [ '视觉中国事件', '复联4','996事件','奔驰女车主维权']

    for event in event_list:
        print(event,"开始")
        # 爬取的新闻路径
        newsPath = os.path.join(os.path.join(dirName, 'EventM\EventMonitor\\news'), event)
        if not os.path.exists(newsPath):
            os.makedirs(newsPath)
        # print("newsPath", newsPath)

        # 存储结果路径
        outPath = os.path.join(os.path.join(curPath, 'output'), event)
        # print("outPath拼接", outPath)
        if not os.path.exists(outPath):
            os.makedirs(outPath)

        storyPath = os.path.join(os.path.join(curPath, 'story'), event)
        # print("storyPath", storyPath)
        if not os.path.exists(storyPath):
            os.makedirs(storyPath)

        handler = Docrank(newsPath,storyPath,outPath)
        doc_graph = handler.doc_graph()
        timelines = handler.timeline(doc_graph)
        sumary = handler.getSummary()
        print(event, "结束")

if __name__ == '__main__':
    main()




