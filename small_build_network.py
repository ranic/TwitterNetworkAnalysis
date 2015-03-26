""" small_build_network.py

    Input: File containing a list of hashtags
    Expects: (existence of) files graphs/<hashtag>/nodes{1,2,3}.csv, graphs/<hashtag>/edges3.csv
    Output: Files graphs/<hashtag>/edges{1,2}.csv containing edge lists for each timestamp
"""
from collections import defaultdict
import sys

NUM_WINDOWS = 10

# Read hashtags
with open(sys.argv[1], 'r') as f:
    hashtags = map(lambda x: x[:-1], f.readlines())

# Stream through all_edges for a hashtag and partition by time slice
for hashtag in hashtags:
    node_sets = []
    edge_sets = [set() for _ in xrange(NUM_WINDOWS)]
    for i in xrange(NUM_WINDOWS):
        with open('graphs/%s/nodes%d.csv' % (hashtag, i+1), 'r') as f:
            node_sets.append(set(map(lambda x: x.strip(), f.readlines())))

    # Read all edges
    with open('graphs/%s/all_edges.csv' % hashtag, 'r') as f:
        all_edges = f.readlines()

    for line in all_edges:
        # Copy edges corresponding to nodes in lower time slices
        (follower, _, user) = line.strip().partition("\t")

        for i in xrange(NUM_WINDOWS):
            if (user in node_sets[i] and follower in node_sets[i]):
                edge_sets[i].add(line)

    for i in xrange(NUM_WINDOWS):
        with open('graphs/%s/edges%d.csv' % (hashtag, i+1), 'w') as f:
            f.write("".join(edge_sets[i]))
