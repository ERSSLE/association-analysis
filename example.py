# encoding: utf-8
"""
关联分析案例
"""

# original author information
__copyright__ = 'Copyright © 2022 ERSSLE'
__license__ = 'MIT License'

import pandas as pd
inputfile = 'example_data.txt'
datas = pd.read_csv(inputfile,header=None).values
datas_size = len(datas)

import apriori
import fp_growth
import fp_growth2
import rule

minimum_support = 0.05
minimum_confidence = 0.5
minimum_lift = None

itemsets = rule.find_frequent_itemsets(apriori.find_frequent_itemsets,datas,minimum_support)
# or itemsets = rule.find_frequent_itemsets(fp_growth2.find_frequent_itemsets,datas,minimum_support)
# or itemsets = list(rule.find_frequent_itemsets(fp_growth.find_frequent_itemsets,datas,minimum_support))

rules = rule.find_rules(itemsets,datas_size,minimum_confidence,minimum_lift,corr=rule.Evatn_func.corr)
print('关联规则即其伴随的度量值：')
for i in range(10):
    print(next(rules))
print()
print('有关频繁项的r支持度比率与h置信度，用以衡量交叉支持模式：\n',rule.find_r_h(itemsets)[:10])
