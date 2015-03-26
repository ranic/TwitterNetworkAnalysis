""" build_network.py

    Input: File containing a list of hashtags
    Expects: (existence of) files graphs/<hashtag>/nodes{1,2,3}.csv
    Output: Files graphs/<hashtag>/edges3.csv containing edge lists for each network
"""
import sys, os, json
from collections import defaultdict

NUM_LINES = 284884514
CACHE_LIMIT = 100000
NUM_WINDOWS = 10

# Node and edge sets
nodes_for_hashtag = defaultdict(set)
edges_for_hashtag = defaultdict(set)

def flush_cache():
    print >> sys.stderr, "Flushing edges"
    for hashtag in hashtags:
        with open("graphs/%s/all_edges.csv" % hashtag, 'a') as e:
            e.write("\n".join(edges_for_hashtag[hashtag]))
    edges_for_hashtag.clear()

def get_cache_size():
    return sum([len(v) for _,v in edges_for_hashtag.iteritems()])

# Read hashtags
with open(sys.argv[1], 'r') as f:
    hashtags = map(lambda x: x[:-1], f.readlines())

# Build node sets for each hashtag
for hashtag in hashtags:
    for i in xrange(NUM_WINDOWS):
        with open("graphs/%s/nodes%d.csv" % (hashtag, i+1), 'r') as f:
            nodes_for_hashtag[hashtag].update(set(map(lambda x: x.strip(), f.readlines())))
    # Clear previous contents of edge sets
    with open("graphs/%s/all_edges.csv" % hashtag, 'w') as f:
        pass


# Stream through entire Twitter network and pull out edges relevant to input hashtags
count = 0
with open("big_data/network.txt", 'r') as f:
    while (count < NUM_LINES):
        line = f.readline().strip()
        (node, _ , follower) = line.partition("\t")

        # If edge is in a hashtag's network, add it to the edge set
        for hashtag, nodes in nodes_for_hashtag.iteritems():
            if (node in nodes and follower in nodes):
                edges_for_hashtag[hashtag].add("%s\t%s" % (follower, node))

        count += 1
        if ((count % 1000000) == 0):
            print >> sys.stderr, "%d lines read." % count

        if (get_cache_size() > CACHE_LIMIT):
            flush_cache()

flush_cache()
