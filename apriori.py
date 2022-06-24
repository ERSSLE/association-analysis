# encoding: utf-8
"""
通过apriori算法寻找购物篮数据当中的频繁项集

"""

# original author information
__copyright__ = 'Copyright © 2022 ERSSLE'
__license__ = 'MIT License'

import numpy as np
def gen_items(transactions):
    """获取唯一的项数目与数据条目数量"""
    items = []
    for i,transaction in enumerate(transactions):
        for item in transaction:
            if item not in items:
                items.append(item)
    return items,i+1

def gen_matrix(transactions):
    """通过购物篮类数据创建np.array"""
    items,length = gen_items(transactions)
    matrix = np.zeros((length,len(items)))
    for row_idx,transaction in enumerate(transactions):
        for item in transaction:
            col_idx = items.index(item)
            matrix[row_idx,col_idx] = 1
    return matrix,np.asarray(items)

def find_frequent_itemsets(transactions,minimum_support):
    """
    基于给定的支持度，查找频繁项集
    transactions: 类双层python链表，每一项元素代表一条数据
    minimum_support: 支持度
    """
    matrix,items = gen_matrix(transactions)
    cnts = matrix.sum(0)
    mask = cnts >= minimum_support
    matrix = matrix[:,mask] # 根据最小支持度筛选matrix
    items = items[mask] # 根据最小支持度筛选items
    cnts = cnts[mask] # 根据最小支持度初步筛选cnts

    # 特定长度频繁项集，这里长度为1，即Fk = 1
    frequent_items_alpha = [(np.asarray([items.tolist().index(item)]),int(cnt)) for item,cnt in zip(items,cnts)]
    # 用于存储所有的频繁项集
    frequent_items = []
    frequent_items.append(frequent_items_alpha)
    while True:
        frequent_items_k_1 = frequent_items[-1] # 上一轮频繁项集
        items_length = len(frequent_items_k_1) # 上一轮频繁项集个数
        item_num = len(frequent_items_k_1[0][0]) + 1 # 本轮频繁项集长度
        frequent_items_alpha = [] # 特定长度频繁项集，这里长度为>=2，即Fk >= 2
        count = [] # 存储支持度
        
        # 新长度下频繁项集产生基于Fk-1 x Fk-1策略，详细可以查看《数据挖掘导论(完整版)》Pang-Ning Tan,
        # Michael Steinbach, Vipin Kunmar著 6.2.3小节
        for i in range(items_length-1):
            for j in range(i+1,items_length):
                left_item = frequent_items_k_1[i][0]
                right_item = frequent_items_k_1[j][0]
                if item_num >= 3:
                    condition = (left_item[:-1] == right_item[:-1]).all() and (left_item[-1] != right_item[-1])
                else:
                    condition = left_item[-1] != right_item[-1]
                if condition:
                    candidate = np.append(left_item,right_item[-1])
                    cnt = (matrix[:,candidate].sum(1) == item_num).sum()
                    if cnt >= minimum_support:
                        frequent_items_alpha.append(candidate)
                        count.append(cnt)
        if len(frequent_items_alpha) > 0: #查找至空结束
            frequent_items_alpha = list(zip(frequent_items_alpha,count))
            frequent_items.append(frequent_items_alpha)
        else:
            break
    return [([items[idx] for idx in fi[0]],fi[1]) for fis in frequent_items for fi in fis]

if __name__ == '__main__':
    datas = [
        ['a','b'],
        ['b','c','d'],
        ['a','c','d','e'],
        ['a','d','e'],
        ['a','b','c'],
        ['a','b','c','d'],
        ['a'],
        ['a','b','c'],
        ['a','b','d'],
        ['b','c','e']
    ]
    print('datas频繁项集:','\n',find_frequent_itemsets(datas,2))
