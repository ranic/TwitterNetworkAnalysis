""" analysis.py 

Input: File containing list of hashtags to analyze

Output: Files containing network statistics for each hashtag (stats/<hashtag>.out) and plots of the various network statistics over time (visualizations/<hashtag>.png). Assumes existence of hashtag graphs in graphs/<hashtag>/* 
"""
import networkx as nx
import sys
import signal
import matplotlib.pyplot as plt
import numpy as np
import pickle
import json
import community
from collections import defaultdict

TIMEOUT = 100

### TIMEOUT HANDLER (TODO: Export to another file) ###

def handler(signum, frame):
    print "Timed out"
    raise Exception("Time out")

signal.signal(signal.SIGALRM, handler)

def get_shortest_path(g):
    result = 0
    try:
        signal.alarm(TIMEOUT)
        result = nx.average_shortest_path_length(g)
    except Exception:
        result = 0
    finally:
        signal.alarm(0)
        return result

### END TIMEOUT HANDLER ###

### NETWORK STATISTICS CONTAINER CLASS ###
class NetworkStats:
    """ Container for statistics about a particular network """
    def __init__(self, hashtag, G):
        self.hashtag = hashtag
        y = [get_shortest_path(comp) for comp in nx.connected_component_subgraphs(G) if len(comp) > 1]
        x = filter(lambda t: t > 0, y)
        self.degrees = nx.degree(G).values()

        # The following statistics are plotted
        self.average_path_length = sum(x)/len(x) if len(x) > 0 else 0
        self.clustering = nx.average_clustering(G)
        self.avg_degree = sum(self.degrees)/len(self.degrees)
        self.modularity = community.modularity(community.best_partition(G), G)
        self.diameter = max([nx.diameter(comp) for comp in nx.connected_component_subgraphs(G)])

    def __str__(self):
        return "Clustering: %s\nAverage Path Length: %s\nAverage Degree: %s\n\
        Modularity: %s\nNetwork Diameter: %s \n\n" % (self.clustering, self.average_path_length, self.avg_degree, self.modularity, self.diameter)

class NetworkStatsList:
    def __init__(self, hashtag, stats_list, time_slices):
        self.hashtag = hashtag
        self.stats = stats_list
        self.time_slices = time_slices

    def __str__(self):
        return "%s\n%s" % (hashtag, "\n".join(["%s\n\n%s\n" % (time_slices[i], self.stats[i]) for i in xrange(len(self.stats))]))

### END NETWORK STATISTICS CONTAINER CLASS ###

### HELPER FUNCTIONS ###
def build_network_from_nodes_and_edges(hashtag, i):
    """ Builds and returns a NetworkX graph from the node/edge list for <hashtag> at time slice <i> """
    G = nx.Graph()

    with open("graphs/%s/nodes%d.csv" % (hashtag, i), "r") as f:
        [G.add_node(x.strip()) for x in f.readlines()]

    with open("graphs/%s/edges%d.csv" % (hashtag, i), "r") as f:
        lines = map(lambda x: x.strip(), f.readlines())
        print "Adding edges for hashtag ", hashtag
        for line in lines:
            (x, _, y) = line.partition("\t")
            G.add_edge(x,y)
    
    return G

def visualize_statistics(stats_list, out_file):
    """ Plots the dynamic statistics for a hashtag to out_file """
    x_axis = range(3)
    x_ticks = stats_list.time_slices

    # Get dynamic statistics
    average_path_length = [s.average_path_length for s in stats_list.stats]
    clustering = [s.clustering for s in stats_list.stats]
    diameter = [s.diameter for s in stats_list.stats]
    modularity = [s.modularity for s in stats_list.stats]
    avg_degree = [s.avg_degree for s in stats_list.stats]

    # Graph the results using pyplot
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx() # for smaller numbers
    l2 = ax1.plot(x_axis, clustering, 'bs-', label='Clustering Coefficient')
    l4 = ax1.plot(x_axis, modularity, 'b^-', label='Modularity')
    l1 = ax2.plot(x_axis, average_path_length, 'rs-', label='Average Path Length')
    l3 = ax2.plot(x_axis, diameter, 'r^-', label='Diameter')
    l5 = ax2.plot(x_axis, avg_degree, 'rd-', label='Avg Degree')

    # Shrink current axis by 20%
    box = ax1.get_position()
    ax1.set_position([box.x0, box.y0+10, box.width * 0.75, box.height])
    box = ax2.get_position()
    ax2.set_position([box.x0, box.y0+10, box.width * 0.75, box.height])

    # Put a legend to the right of the current axis
    plt.setp(ax1, xticks=x_axis, xticklabels=x_ticks)
    lns = l1 + l2 + l3 + l4 + l5
    labs = [l.get_label() for l in lns]
    legend = ax1.legend(lns, labs, loc='center left', bbox_to_anchor=(1.05, 0.5))

    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    for t2 in ax2.get_yticklabels():
        t2.set_color('r')

    [x1,x2,y1,y2] = plt.axis()
    plt.axis([x1, x2, y1 - 1, y2 + 1])

    # Label the graph
    ax1.set_title("'%s' - Dynamic Network Characteristics" % stats_list.hashtag)
    plt.xlabel('Time slice')
    ax1.set_ylabel('Network Statistic Value')
    
    # Save to out_file
    plt.savefig(out_file, bbox_extra_artists=(legend,), bbox_inches='tight')


### END HELPER FUNCTIONS ###

if __name__ == "__main__":
    # Read in hashtags to analyze
    if (len(sys.argv) == 2):
        with open(sys.argv[1], "r") as f:
            hashtags = map(lambda x: x.strip(), f.readlines())
       
        # Maps hashtags to a NetworkStatsList object
        dynamic_stats_for_hashtag = dict()

        for hashtag in hashtags:
            # Get time slices for this hashtag
            with open("graphs/%s/times.csv" % hashtag, "r") as f:
                time_slices = json.load(f)

            stats_list = []
            for i in xrange(1,4):
                # Construct graph for this hashtag at timestamp i
                G = build_network_from_nodes_and_edges(hashtag, i)
                # Compute statistics and add to list of statistics
                stats_list.append(NetworkStats(hashtag, G))
            
            dynamic_stats_for_hashtag[hashtag] = NetworkStatsList(hashtag, stats_list, time_slices)
            with open('stats/readable_%s.out' % hashtag, 'w') as f:
                f.write(str(dynamic_stats_for_hashtag[hashtag]))

        # At this point, statistics have been computed for all hashtags. Serialize
        with open('stats/all_statistics.out', 'w') as f:
            pickle.dump(dynamic_stats_for_hashtag, f)
    else:
        # Read in the previously computed statistics and proceed to visualization
        with open('stats/all_statistics.out', 'r') as f:
            dynamic_stats_for_hashtag = pickle.load(f)

    # Store visualizations of data
    for hashtag, stats in dynamic_stats_for_hashtag.iteritems():
        visualize_statistics(stats, "visualizations/%s.png" % hashtag)
