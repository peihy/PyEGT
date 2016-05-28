# -*- coding: utf-8 -*-
# -*- Author: shaodan(shaodan.cn@gmail.com) -*-
# -*-  2015.07.11 -*-

import numpy as np
import networkx as nx


class Game(object):
    """base_game"""

    def __init__(self):
        pass

    # 博弈过程，必须继承
    def play(self, graph, strategy, fitness, node_list=None, edge_list=None):
        if node_list is None:
            # 初始化fitness，整体进行一次博弈
            pass
        elif node_list:
            # 局部更新
            self.fast_play(graph, strategy, fitness, node_list, edge_list)

    def fast_play(self, graph, strategy, fitness, node_list, edge_list=None):
        # todo : 会有精度差别 10^-16~-15数量级
        if not isinstance(node_list, list):
            # 先转换成list
            node_list = [node_list]
        for node in node_list:
            pass


class PGG(Game):
    """public_goods_game"""

    def __init__(self, r=2, fixed=False):
        super(self.__class__, self).__init__()
        # 获利倍数
        self.r = float(r)
        self.fixed = fixed

    def play(self, graph, strategy, fitness, node_list=None, edge_list=None):
        # 可能会有负的fitness
        if node_list is None:
            fitness.fill(0)
            # 第一种每个group投入1
            degrees = np.array(graph.degree().values())
            for node in graph.nodes_iter():
                degree = degrees[node]
                fitness[node] += (strategy[node]-1) * (degree+1)
                neighs = graph.neighbors(node)
                neighs.append(node)
                # b = self.r * (strategy[neighs]==0).sum() / (degree+1)
                b = self.r * (len(neighs)-np.count_nonzero(strategy[neighs])) / (degree+1)
                for neigh in neighs:
                    fitness[neigh] += b
            # 第二种每个group投入1/(k+1)
            # degrees = np.array(G.degree().values())
            # inv = (1.0-strategy) / (degrees+1)
            # for node in G.nodes_iter():
            #     fitness[node] += strategy[node] - 1
            #     neighs = G.neighbors(node)
            #     neighs.append(node)
            #     b = self.r * inv[neighs].sum() / (degrees[node]+1)
            #     for neigh in neighs:
            #         fitness[neigh] += b
        else:
            self.fast_play(graph, strategy, fitness, node_list)

    def fast_play(self, graph, strategy, fitness, node_list, edge_list=None):
        if not isinstance(node_list, list):
            node_list = [node_list]
        for node in node_list:
            s = strategy[node]
            sign = (1 - 2*s)
            sign_r = sign * self.r
            d = graph.degree(node)
            # 更新节点作为中心pgg产生的收益增量
            delta = sign_r/(d+1)
            fitness[node] += delta - sign*(d+1)
            for neigh in graph.neighbors_iter(node):
                delta_neigh = sign_r/(graph.degree(neigh)+1)
                fitness[neigh] += delta + delta_neigh
                for neigh_neigh in graph.neighbors_iter(neigh):
                    fitness[neigh_neigh] += delta_neigh


class PDG(Game):
    """prisoner's_dilemma_game"""

    def __init__(self, r=1, t=1.5, s=0, p=0.1):
        super(self.__class__, self).__init__()
        self.payoff = np.array([[(r, r), (s, t)], [(t, s), (p, p)]], dtype=np.double)
        self.delta = t-s

    def play(self, graph, strategy, fitness, node_list=None, edge_list=None):
        if node_list is None:
            fitness.fill(0)
            for edge in graph.edges_iter():
                a = edge[0]
                b = edge[1]
                p = self.payoff[strategy[a]][strategy[b]]
                fitness[a] += p[0]
                fitness[b] += p[1]
        else:
            self.fast_play(graph, strategy, fitness, node_list)

    def fast_play(self, graph, strategy, fitness, node_list, edge_list=None):
        if not isinstance(node_list, list):
            node_list = [node_list]
        # 只用计算新节点和其邻居节点的收益
        # 如果node_list为空list，则不更新
        for node in node_list:
            f = 0  # 新节点收益从0计算
            s = strategy[node]
            s_ = 1 - s
            for neigh in graph.neighbors_iter(node):
                p = self.payoff[s][strategy[neigh]]
                f += p[0]           # 新节点累加
                new_payoff = p[1]   # 邻居节点计算新的收益
                # 0合作，1背叛
                p = self.payoff[s_][strategy[neigh]]
                old_payoff = p[1]   # 邻居节点计算原来的收益
                fitness[neigh] += new_payoff - old_payoff
            fitness[node] = f


class RPG(Game):
    name = "Rational Player Game"

    def __init__(self, ration):
        super(self.__class__, self).__init__()
        self.ration = ration

    def play(self, graph, strategy, fitness, node_list=None, edge_list=None):
        pass


class IPD(Game):

    def __init__(self):
        super(self.__class__, self).__init__()

# TEST CODE HERE
if __name__ == '__main__':
    # g = PDG()
    g = PGG(2)
    G = nx.random_regular_graph(5, 100)
    st = np.random.randint(2, size=100)
    fit = np.empty(100)
    g.play(G, st, fit)
    print fit

    i = np.random.randint(100)
    st[i] = 1-st[i]
    fit1 = fit.copy()
    fit2 = fit.copy()
    print "=======fit1==========="
    print fit1
    print "=======fit2==========="
    print fit2
    g.play(G, st, fit1, i)
    g.play(G, st, fit2)

    print "=======delt==========="
    print (fit1-fit2)
    print "=======sum==========="
    print (fit1-fit2).sum()

    print (fit1[i] - fit2[i])
    print G.degree(i)