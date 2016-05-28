# -*- coding: utf-8 -*-
# -*- Author: shaodan -*-
# -*-  2015.07.11 -*-

import numpy as np
import networkx as nx


class Adapter(object):
    def __init__(self, order):
        self.order = order

    # prefer优先策略，anchor重连节点
    def adapt(self, graph, prefer, anchor=None, source=None):
        pass


class LocalAdapter(Adapter):

    def adapt(self, graph, prefer, anchor=None, source=None):
        size = len(graph)
        if anchor is None or source is None:
            return None
        alter = graph.neighbors(source)
        new = None
        if prefer == 0:
            new = np.random.choice(alter)
        elif prefer == 1:
            new = np.random.choice(alter)
        else:
            new = 1
        old = 0
        return old, new


class GlobalAdapter(Adapter):

    def adapt(self, graph, prefer, anchor=None, source=None):
        size = len(graph)


class Preference(Adapter):

    def __init__(self, order=4):
        super(self.__class__, self).__init__(order)

    def adapt(self, graph, prefer, anchor=None, source=None):
        size = len(graph)
        if anchor is None:
            return None
        p = []
        if prefer == 0:    # 随机选择
            p = np.ones(size)
        elif prefer == 1:  # 度优先
            p = np.array(graph.degree().values(), dtype=np.float64)
        elif prefer == 2:  # 相似度
            p = np.array([len(list(nx.common_neighbors(graph, anchor, x))) for x in graph.nodes_iter()],
                         dtype=np.float64)
            p += 1         # 防止没有足够公共节点的
        elif prefer == 3:
            pass
        elif prefer == 4:
            pass
        p[anchor] = 0
        p /= float(p.sum())
        old = np.random.choice(graph.neighbors(anchor))
        new = np.random.choice(size, replace=False, p=p)
        graph.remove_edge(anchor, old)
        graph.add_edge(anchor, new)
        return old, new

    def adapt_one(self, graph, prefer, anchor):
        size = len(graph)
        # rewire only one link
        p = []
        if prefer == 0:
            p = np.ones(size)
        elif prefer == 1:
            p = np.array(graph.degree().values(), dtype=np.float64)
        else:
            pass
        p[anchor] = 0
        p /= float(p.sum())
        new_neigh = np.random.choice(size, p=p)
        k = graph.degree(anchor)
        graph.remove_edges(graph.edges(anchor)[np.random.choice(k)])
        graph.add_edge(anchor, new_neigh)


if __name__ == '__main__':
    G = nx.random_regular_graph(5, 100)
    fitness = np.random.randint(1, 3, size=100) * 1.0
