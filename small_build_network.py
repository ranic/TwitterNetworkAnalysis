""" small_build_network.py

    Input: File containing a list of hashtags
    Expects: (existence of) files graphs/<hashtag>/nodes{1,2,3}.csv, graphs/<hashtag>/edges3.csv
    Output: Files graphs/<hashtag>/edges{1,2}.csv containing edge lists for each timestamp
"""
from collections import defaultdict
import sys

# Read hashtags
with open(sys.argv[1], 'r') as f:
    hashtags = map(lambda x: x[:-1], f.readlines())

# Stream through big edges and take edges with nodes in little edges
for hashtag in hashtags:
    edges_one = set()
    edges_two = set()

    # Read sets of nodes from time slices one and two
    with open('graphs/%s/nodes1.csv' % hashtag, 'r') as f:
        nodes_one = set(map(lambda x: x.strip(), f.readlines()))
    with open('graphs/%s/nodes2.csv' % hashtag, 'r') as f:
        nodes_two = set(map(lambda x: x.strip(), f.readlines()))
    
    # Read all edges
    with open('graphs/%s/edges3.csv' % hashtag, 'r') as f:
        all_edges = f.readlines()

    for line in all_edges:
        # Copy edges corresponding to nodes in lower time slices
        (follower, _, user) = line.strip().partition("\t")
        if (user in nodes_one and follower in nodes_one):
            edges_one.add(line)
        if (user in nodes_two and follower in nodes_two):
            edges_two.add(line)

    with open("graphs/%s/edges1.csv" % hashtag, 'w') as f:
        f.write("Source\tTarget\n")
        f.write("".join(edges_one))

    with open("graphs/%s/edges2.csv" % hashtag, 'w') as f:
        f.write("Source\tTarget\n")
        f.write("".join(edges_two))
