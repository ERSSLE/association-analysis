# encoding: utf-8
"""
对apriori/fp_growth算法寻找的频繁项集,进行关联规则生成

"""

# original author information
__copyright__ = 'Copyright © 2022 ERSSLE'
__license__ = 'MIT License'

from itertools import combinations
from math import sqrt,log

def find_support_from_itemsets(target_set,itemsets):
    """
    查找目标频繁项的支持度计数
    target_set: 目标频繁项
    itemsets: 频繁项集
    """
    target_length = len(target_set)
    target_sup = None
    for itemset in itemsets:
        itemset,sup = itemset
        if target_length == len(itemset):
            checks = []
            for item in target_set:
                checks.append(item in itemset)
            if sum(checks) == target_length:
                target_sup = sup
                break
    return target_sup

def find_rules(itemsets,transactions_size,minimum_conf,minimum_lift=None,**evaluation_funcs):
    """
    根据频繁项集对关联规则的发掘
    itemsets: 频繁项集
    transactions_size: 总数据数量，即数据记录数、行数或条目数
    minimum_conf: 最小接受的置信度
    minimum_lift: 最小接受的提升度，可以不考虑，即为None
    evaluation_funcs: 可自定义的关联规则评价函数，函数必须定义四个位置参数，即便某些不用。在形如A——>B的规则当中：
    四个参数分别指: count(AB),count(A),count(B),count(itemsets)
    常用评估函数可查看Evatn_func
    函数返回：
        (X,Y,support,confidence,lift,[自定义的评价指标])
    """
    evaluation_funcs = list(evaluation_funcs.items())
    funcs_length = len(evaluation_funcs)
    print('return column names：\n 前件——>后件: support,confidence,lift'+',%s'*funcs_length\
         % tuple([func[0] for func in evaluation_funcs]))
    print()
    for itemset in itemsets:
        itemset,sup_count = itemset
        itemset = set(itemset)
        
        length_itemset = len(itemset)
        for size in range(1,length_itemset):
            for left in combinations(itemset,size):
                left = set(left)
                right = itemset.difference(left)
                left_sup_count = find_support_from_itemsets(left,itemsets)
                conf = Evatn_func.conf(sup_count,left_sup_count,None,transactions_size)
                if conf >= minimum_conf:
                    # 计算置信度与提升度
                    right_sup_count = find_support_from_itemsets(right,itemsets)
                    sup = Evatn_func.sup(sup_count,left_sup_count,right_sup_count,transactions_size)
                    lift = Evatn_func.lift(sup_count,left_sup_count,right_sup_count,transactions_size)
                    others = [
                        func[1](sup_count,left_sup_count,right_sup_count,transactions_size)\
                             for func in evaluation_funcs
                    ]
                    if minimum_lift is None or lift >= minimum_lift:
                        yield tuple([left,right,sup,conf,lift] + others)

def find_r_h(itemsets):
    """
    发掘长度>=2的频繁项集的支持度比率r,与h置信度(全置信度)
    itemsets: 频繁项集
    """
    one_itemsets = []
    for itemset in itemsets:
        itemset,sup_count = itemset
        if len(itemset) == 1:
            one_itemsets.append((itemset,sup_count))
    rh = []
    for itemset in itemsets:
        itemset,sup_count = itemset
        if len(itemset) > 1:
            sups = []
            for item in combinations(itemset,1):
                sup = find_support_from_itemsets(list(item),one_itemsets)
                sups.append(sup)
            r = min(sups) / max(sups)
            h = sup_count / max(sups)
            rh.append((itemset,{'r':r,'h':h}))
    return rh

def find_frequent_itemsets(find_func,transactions,minimum_support,**kargs):
    """
    通过特定算法发掘频繁项集;
    minimum_support >= 1且为整数时，代表支持度计数;1.0 >= minimum_support >= 0.0 且为float时代表支持度
    find_func: 可以为apriori,fp_growth2,fp_growth模块下面的同名函数find_frequent_itemsets
    """
    if minimum_support <= 1 and minimum_support >= 0 and type(minimum_support) == float:
        minimum_support = len(transactions) * minimum_support
    itemsets = find_func(transactions,minimum_support,**kargs)
    return itemsets

class Evatn_func(object):
    """
    一些常用的关联规则评估指标：
    sup,conf,lift,corr,IS,alpha,J
    非反演性度量：lift,IS
    非零加性度量：lift,alpha,corr
    非缩放不变性：alpha
    """
    @staticmethod
    def sup(union_count,left_count,right_count,N):
        """频繁项集支持度"""
        return union_count / N

    @staticmethod
    def conf(union_count,left_count,right_count,N):
        """关联规则置信度"""
        return union_count / left_count

    @staticmethod
    def lift(union_count,left_count,right_count,N):
        """关联规则提升度"""
        return (union_count * N) / (left_count * right_count)
    
    @staticmethod
    def corr(union_count,left_count,right_count,N):
        """关联规则相关性"""
        f11 = union_count
        f10 = left_count - union_count
        f01 = right_count - union_count
        f00 = N - (f11 + f10 + f01)
        f1a = left_count
        f0a = N - f1a
        fa1 = right_count
        fa0 = N - fa1
        return (f11*f00 + f01*f10)/sqrt(f1a*fa1*f0a*fa0)

    @staticmethod
    def IS(union_count,left_count,right_count,N):
        """IS度量"""
        return union_count / sqrt(left_count*right_count)

    @staticmethod
    def alpha(union_count,left_count,right_count,N):
        """alpha度量"""
        f11 = union_count
        f10 = left_count - union_count
        f01 = right_count - union_count
        f00 = N - (f11 + f10 + f01)
        return (f11*f00) / (f10*f01)

    @staticmethod
    def J(union_count,left_count,right_count,N):
        """J度量"""
        f11 = union_count
        f10 = left_count - union_count
        f01 = right_count - union_count
        f00 = N - (f11 + f10 + f01)
        f1a = left_count
        f0a = N - f1a
        fa1 = right_count
        fa0 = N - fa1
        return (f11/N)*log(N*f11/(f1a*fa1)) + (f10/N)*log(N*f10/(f1a*fa0))
