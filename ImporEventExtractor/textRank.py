#!/usr/bin/env python
# encoding: utf-8
'''
@author: mengmeng-guo
@project: KG
@file: textRank.py
@time: 2019/4/10 13:46
@desc:
'''
'''
使用textrank方法抽取关键词
'''
'''
TextRank实现步骤如下：     

（1）把给定的文本按照完整的句子进行分割；

（2）对每个句子进行分词和词性标注，过滤停用词，只保留特定词性；

（3）构建候选关键词图G=(V, E)，首先生成关键词集（（2）生成），然后采用共现关系构造两点之间的边，两个节点之间边

仅在对应词汇长度为K的窗口中出现，K表示窗口大小；

（4）迭代传播各节点的权重，直至收敛

（5）对节点权重进行排序，得到最重要的T个词；

（6）由（5）得到的T个词，在原始文本进行标记，若形成相邻词组，则组合成多词关键词。

'''

import jieba
import jieba.posseg
from collections import defaultdict


# 定义无向有权图
class UndirectWeightGraph:
    d = 0.05

    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self, start, end, weight):  # 添加无向图边
        self.graph[start].append((start, end, weight))
        self.graph[end].append((end, start, weight))

    def rank(self):  # 根据文本无向图进行单词权重排序，其中包含训练过程
        ws = defaultdict(float)  # pr值列表
        outSum = defaultdict(float)  # 节点出度列表

        ws_init = 1.0 / (len(self.graph) or 1.0)  # pr初始值
        for word, edge_lst in self.graph.items():  # pr, 出度列表初始化
            ws[word] = ws_init
            outSum[word] = sum(edge[2] for edge in edge_lst)

        sorted_keys = sorted(self.graph.keys())
        for x in range(10):  # 多次循环计算达到马尔科夫稳定
            for key in sorted_keys:
                s = 0
                for edge in self.graph[key]:
                    s += edge[2] / outSum[edge[1]] * ws[edge[1]]
                ws[key] = (1 - self.d) + self.d * s

        min_rank, max_rank = 100, 0

        for w in ws.values():  # 归一化权重
            if min_rank > w:
                min_rank = w
            if max_rank < w:
                max_rank = w
        for key, w in ws.items():
            ws[key] = (w - min_rank) * 1.0 / (max_rank - min_rank)

        return ws


import os


class KeywordExtractor(object):  # 加载停用词表
    stop_words = set()

    def set_stop_words(self, stop_word_path):
        if not os.path.isfile(stop_word_path):
            raise Exception("jieba: file does not exit: " + stop_word_path)
        f = open(stop_word_path, "r", encoding="utf-8")
        for lineno, line in enumerate(f):
            self.stop_words.add(line.strip("\n"))
        return self.stop_words


class TextRank(KeywordExtractor):
    def __init__(self, stop_word_path=None):
        self.tokenizer = self.postokenizer = jieba.posseg.dt
        if not stop_word_path:
            stop_word_path = r"E:\学习相关资料\NLP\停用词表\stopwords-master\百度停用词表.txt"
        self.stop_words = KeywordExtractor.set_stop_words(self, stop_word_path=stop_word_path)
        self.pos_filter = frozenset(("ns", "n", "vn", "v"))
        self.span = 5

    def pairfilter(self, wp):  # wp 格式为 (flag, word)
        state = (wp.flag in self.pos_filter) and (len(wp.word.strip()) >= 2) and (
        wp.word.lower() not in self.stop_words)
        # print("1:", state)
        return state

    def textrank(self, sentence, topK=20, withWeight=False, allowPOS=("ns", "n", "vn", "v")):
        self.pos_filt = frozenset(allowPOS)
        g = UndirectWeightGraph()
        word2edge = defaultdict(int)
        words = tuple(self.tokenizer.cut(sentence))
        for i, wp in enumerate(words):  # 将句子转化为边的形式
            # print(wp.flag, wp.word)
            if self.pairfilter(wp):
                for j in range(i + 1, i + self.span):
                    if j >= len(words):
                        break
                    if not self.pairfilter(words[j]):
                        continue
                    word2edge[(wp.word, words[j].word)] += 1

        for terms, w in word2edge.items():
            g.addEdge(terms[0], terms[1], w)
        nodes_rank = g.rank()
        if withWeight:
            tags = sorted(nodes_rank.items(), key=lambda x: x[1], reverse=True)
        else:
            tags = sorted(nodes_rank)
        if topK:
            return tags[: topK]
        else:
            tags


stop_word_path = r"D:\Users\mengmeng-guo\PycharmProjects\KG\word\百度停用词表.txt"
sentence = r"上海一银行女员工将银行1亿多人民币据为已有，海内外购置10多套房产"
extract_tags = TextRank(stop_word_path=stop_word_path).textrank
print(extract_tags(sentence=sentence, topK=2, withWeight=False))