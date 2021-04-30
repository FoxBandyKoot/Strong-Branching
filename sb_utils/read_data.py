import os

import pandas as pd

from sb_utils.node import BBNode

def read_all_dfs(path):
    dfs = {}
    for file in os.listdir(path):
        dfs[file] = pd.read_csv(os.path.join(path, file))
    return dfs

def build_bbtree(df, filename):
    """
    Build the Branch and Bound tree for the given df.
    """
    feature_name = [f for f in df.columns
                    if f not in {'node_number', 'parent_node_number', 'value'}]
    
    nodes = dict()  # node_id -> BBNode
    parent_map = dict()  # node_id -> parent_id
        
    # Build all BBNodes
    for i in range(len(df)):
        node_id = df.loc[i, 'node_number']
        parent_id = df.loc[i, 'parent_node_number']
        value = df.loc[i, 'value']
        features = dict(df.loc[i, feature_name])
        node = BBNode(filename, node_id, features, value)

        nodes[node_id] = node
        parent_map[node_id] = parent_id

    # Link BBNodes to their parent
    for node_id, node in nodes.items():
        parent_id = parent_map[node_id]
        if parent_id in nodes:
            parent_node = nodes[parent_id]
            parent_node.add_child(node)

    return nodes

def keep_parent_nodes(nodes):
    """
    Filter all nodes in the dictionary, to keep only
    the nodes that are parent to some other nodes.
    """
    parents_id = set(n_id for n_id, n in nodes.items()
                     if n.children_nodes)
    return {p_id: parent for p_id, parent in nodes.items()
            if p_id in parents_id}

def get_trees(path):
    dfs = read_all_dfs(path)
    trees = {f: build_bbtree(df, f) for f, df in dfs.items()}
    trees = {f: keep_parent_nodes(nodes) for f, nodes in trees.items()}
    return trees