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
minimum_lift = 1.2

itemsets = rule.find_frequent_itemsets(apriori.find_frequent_itemsets,datas,minimum_support)
# or itemsets = rule.find_frequent_itemsets(fp_growth2.find_frequent_itemsets,datas,minimum_support)
# or itemsets = list(rule.find_frequent_itemsets(fp_growth.find_frequent_itemsets,datas,minimum_support))
rules = rule.find_rules(itemsets,datas_size,minimum_confidence,minimum_lift)

rules = pd.DataFrame(rules,columns=['前件','后件','support','confidence','lift'])
print(rules)
