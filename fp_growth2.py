# encoding: utf-8
"""
通过fp-growth算法寻找购物篮数据当中的频繁项集，算法逻辑来源于：Tan, Pang-Ning, Michael Steinbach, and Vipin Kumar. 
Introduction to Data Mining. 1st ed. Boston: Pearson / Addison Wesley, 2006. (pp. 363-370)

"""

# original author information
__copyright__ = 'Copyright © 2022 ERSSLE'
__license__ = 'MIT License'

from collections import defaultdict

class FPTree(object):
    """
    创建一颗FP树，算法的逻辑来源于 Tan, Pang-Ning, Michael Steinbach, and Vipin Kumar. 
    Introduction to Data Mining. 1st ed. Boston: Pearson / Addison Wesley, 2006. (pp. 363-370)
    """
    def __init__(self,reverse=True):
        """
        初始化：reverse指定树生长时的排序方式，默认从高频项到低频项，也可反转（False）
        """
        self._reverse = reverse
        self._nodes_level = defaultdict(lambda: set())
        self._nodes_cluster = defaultdict(lambda: set())
        self._nodes_parent = defaultdict(lambda: None)
        self._nodes_children = defaultdict(lambda: set())
        self._nodes_count = defaultdict(lambda: 0)
        
        self._nodes_level['lv_0'].add(0)
        self._nodes_cluster['root'].add(0)
        self._nodes_parent[0] = None
        self._nodes_children[0] = set()
        self._nodes_count[0] = None
        
    @property
    def node_datas(self):
        """
        返回所含所有fp树结构信息的数据
        """
        return dict(
            nodes_level = dict(self._nodes_level),
            nodes_cluster = dict(self._nodes_cluster),
            nodes_parent = dict(self._nodes_parent),
            nodes_children = dict(self._nodes_children),
            nodes_count = dict(self._nodes_count)
        )
        
    def create_tree(self,node_datas):
        """
        根据结构数据直接构建fp树
        node_datas:一个字典结构数据，其形式与node_datas返回结果相同
        """
        self._nodes_level = node_datas['nodes_level']
        self._nodes_cluster = node_datas['nodes_cluster']
        self._nodes_parent = node_datas['nodes_parent']
        self._nodes_children = node_datas['nodes_children']
        self._nodes_count = node_datas['nodes_count']
        
    def add(self,transaction):
        """
        逐条添加
        """
        last_node = 0
        for i,item in enumerate(transaction):
            node = self._nodes_cluster[item].intersection(self._nodes_children[last_node])
            if node:
                node = list(node)[0]
                self._nodes_count[node] += 1
            else:
                node = self._next_node
                self._nodes_level['lv_%s' % (i+1)].add(node)
                self._nodes_cluster[item].add(node)
                self._nodes_parent[node] = last_node
                self._nodes_children[last_node].add(node)
                self._nodes_count[node] += 1
            last_node = node
    def adds(self,transactions,support=1):
        """
        输入数据条目，生长fp树
        transactions: 双层python链表，内嵌层每一项元素代表一条数据
        support:项的最小支持度
        """
        items = defaultdict(lambda: 0)
        for transaction in transactions:
            for item in transaction:
                assert item != 'root','数据当中不可存在root默认的根节点标识，尝试替换成其它标识后再进行'
                items[item] += 1
        items = dict((item, spt) for item, spt in items.items() if spt >= support)
        self.item_list = [k for k in items.keys()]
        self.item_list.sort(key=lambda k: items[k],reverse=self._reverse)
        self.item_list.append(None)  # 添加虚拟待检查节点，使fp全树的频繁项集查找和子图统一
        def clean_transaction(transaction):
            transaction = filter(lambda v: v in items, transaction)
            transaction_list = list(transaction)
            transaction_list.sort(key=lambda v: items[v], reverse=self._reverse)
            return transaction_list
        for transaction in map(clean_transaction,transactions):
            self.add(transaction)
            
    @property
    def _next_node(self):
        """
        返回下一个节点id号，每一个节点有一个唯一的id号,root节点id=0
        """
        return max(self._nodes_parent) + 1
    @property
    def maxdepth(self):
        """排除根节点树结构的最大深度"""
        return len(self._nodes_level) - 1
    @property
    def node_num(self):
        """排除根节点树的节点总数"""
        return len(self._nodes_parent) - 1
        
def find_child_tree(tree,item,node_to_item=None):
    """
    根据结尾项从源树获取子树，使子树的叶节点均含有类型相同的项
    tree: 源树
    item: 子树的叶节点类型
    node_to_item: 一个从节点到节点类型的映射字典，如果为None自动查找
    """
    nodes_cluster = tree.node_datas['nodes_cluster']
    nodes_parent = tree.node_datas['nodes_parent']
    nodes_count = tree.node_datas['nodes_count']
    if node_to_item is None:
        node_to_item = dict((v,k) for k,vs in nodes_cluster.items() for v in vs)
    leaf_nodes = nodes_cluster[item]
    
    child_tree = FPTree()
    new_node_datas = dict(
            nodes_level = defaultdict(lambda: set()),
            nodes_cluster = defaultdict(lambda: set()),
            nodes_parent = defaultdict(lambda: None),
            nodes_children = defaultdict(lambda: set()),
            nodes_count = defaultdict(lambda: 0)
    )
    for node in leaf_nodes:
        nodes = [node]
        while node:
            node = nodes_parent[node]
            nodes.append(node)
        for i,node in enumerate(nodes):
            new_node_datas['nodes_level']['lv_%s' % (len(nodes) - nodes.index(node)-1)].add(node)
            new_node_datas['nodes_cluster'][node_to_item[node]].add(node)
            new_node_datas['nodes_parent'][node] = nodes_parent[node]
            if node > 0:
                new_node_datas['nodes_children'][nodes_parent[node]].add(node)
                new_node_datas['nodes_count'][node] += nodes_count[nodes[0]]
            else:
                new_node_datas['nodes_count'][node] = None
    child_tree.create_tree(new_node_datas)
    child_tree._reverse = tree._reverse
    child_tree.item_list = [item for item in tree.item_list if item in child_tree._nodes_cluster]
    return child_tree

def find_counts(tree,minimum_support,node_to_item=None):
    """
    从树结构当中递归查找频繁项的统计值，即支持度。
    返回结果是一个层叠的字典
    tree: fp树
    minimum_support: 支持度
    node_to_item: 一个从节点到节点类型的映射字典，如果为None自动查找
    """
    if node_to_item is None:
        node_to_item = dict((v,k) for k,vs in tree.node_datas['nodes_cluster'].items() for v in vs)
    def get_count(tree,item):
        return sum(tree.node_datas['nodes_count'][node] for node in tree.node_datas['nodes_cluster'][item])
    def find_trees_count(tree):
        trees = []
        for item in tree.item_list[-2::-1]:
            child_tree = find_child_tree(tree,item,node_to_item)
            if get_count(tree,item) >= minimum_support:
                trees.append(child_tree)
        return {tr.item_list[-1]:(
            get_count(tr,tr.item_list[-1]),
            find_trees_count(tr)
            ) for tr in trees
               }
    return find_trees_count(tree)

def find_frequent_itemsets_alpha(cnt):
    """解析find_count结果，生成频繁项集"""
    itemsets = []
    def find_itemsets(cnt,suffix=[]):
        cnts = []
        for k,vs in cnt.items():
            itemset = ([k] + suffix,vs[0])
            itemsets.append(itemset)
            cnts.append(vs[1])
            find_itemsets(vs[1],[k]+suffix)
    find_itemsets(cnt)
    return itemsets

def find_frequent_itemsets(datas,minimum_support,reverse=True):
    """
    基于给定的支持度，查找频繁项集
    datas: 双层python链表，每一项元素代表一条数据
    minimum_support: 支持度
    reverse: 指定树生长时的排序方式，默认从高频项到低频项，也可反转（False）
    """
    tree = FPTree(reverse=reverse)
    tree.adds(datas,support=minimum_support)
    node_to_item = dict((v,k) for k,vs in tree.node_datas['nodes_cluster'].items() for v in vs)
    counts = find_counts(tree,minimum_support,node_to_item)
    return find_frequent_itemsets_alpha(counts)

try:
    import networkx as nx
    import matplotlib.pyplot as plt

    def plot_fptree(tree,width_depth_rate = 1.5,add_labels=True,ax=None):
        """
        根据给定的fp树绘制成图形
        tree: 树
        add_labels: 添加节点类型与计数标签
        """
        node_datas = tree.node_datas
        node_to_item = dict((v,k) for k,vs in tree._nodes_cluster.items() for v in vs)
        depth = tree.maxdepth
        max_width = max(len(nodes)for nodes in node_datas['nodes_level'].values())
        graph = nx.Graph()
        graph_width = (max_width * width_depth_rate) / depth
        graph_depth = 1.0
        row_num = 1
        nodes_xy = {}
        nodes_labels = []
        def add_nodes(nodes,row_num = row_num):
            width = len(nodes)
            xs = [graph_width * (i+1) / (width+1) for i in range(width)]
            ys = [1 - (graph_depth * row_num) / (depth+2)] * width
            row_num += 1
            nodes_xy.update(dict((node,(x,y)) for node,x,y in zip(nodes,xs,ys) if node is not None))
            for node,x,y in zip(nodes,xs,ys):
                if node is not None:
                    txt = '%s:%s' % (node_to_item[node],node_datas['nodes_count'][node])
                    nodes_labels.append((txt,(x,y)))
            new_nodes = []
            for node in nodes:
                if node in node_datas['nodes_children']:
                    children = sorted(list(node_datas['nodes_children'][node]))
                    if children:
                        new_nodes = new_nodes + children
                    else:
                        new_nodes.append(None)
                else:
                    new_nodes.append(None)
            if set(new_nodes) == set([None]):
                return 0
            else:
                add_nodes(new_nodes,row_num)
        add_nodes([0])
        graph.add_nodes_from(nodes_xy)
        for k,vs in node_datas['nodes_children'].items():
            graph.add_edges_from((k,v) for v in vs)
        if ax is None:
            fig = plt.figure(figsize=(6*graph_width,6))
            ax = fig.add_subplot()
        nx.draw(graph,nodes_xy,with_labels=True,node_size=1000,node_color='r',ax=ax)
        if add_labels:
            for txt,xy in nodes_labels:
                _ = ax.text(xy[0],xy[1]-0.05,txt,fontdict={'fontsize':15,'color':'b'})
except ModuleNotFoundError:
    None

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
    if 'plot_fptree' in dir():
        tree = FPTree()
        tree.adds(datas,2)
        plot_fptree(tree)
        plt.show()
