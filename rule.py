# encoding: utf-8
"""
对apriori/fp_growth算法寻找的频繁项集,进行关联规则生成

"""

# original author information
__copyright__ = 'Copyright © 2022 ERSSLE'
__license__ = 'MIT License'

from itertools import combinations

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

def find_rules(itemsets,transactions_size,minimum_conf,minimum_lift=None):
    """
    根据频繁项集对关联规则的发掘
    itemsets: 频繁项集
    transactions_size: 总数据数量，即数据记录数、行数或条目数
    minimum_conf: 最小接受的置信度
    minimum_lift: 最小接受的提升度，可以不考虑，即为None
    函数返回：
        (X,Y,support,confidence,lift)
    """
    all_rules = []
    for itemset in itemsets:
        itemset,sup_count = itemset
        itemset = set(itemset)
        sup = sup_count / transactions_size # 计算支持度
        length_itemset = len(itemset)
        for size in range(1,length_itemset):
            for left in combinations(itemset,size):
                left = set(left)
                right = itemset.difference(left)
                left_sup_count = find_support_from_itemsets(left,itemsets)
                conf = sup_count / left_sup_count # 计算置信度
                if conf >= minimum_conf:
                    # 计算提升度
                    right_sup_count = find_support_from_itemsets(right,itemsets)
                    right_sup = right_sup_count / transactions_size
                    lift = conf / right_sup 
                    if minimum_lift is None or lift >= minimum_lift:
                        all_rules.append((left,right,sup,conf,lift))
    return all_rules

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
