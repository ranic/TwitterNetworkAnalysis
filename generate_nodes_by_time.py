""" generate_nodes_by_time.py

    Input: File containing a list of hashtags
    Output: Files containing nodes for each hashtag in graphs/<hashtag>/nodes{1,2,3}.csv
"""
import os, sys
import pickle
import time
from Tweet import Tweet
import json

TIME_FORMAT = "%a %b %d %H:%M:%S  %Y"
TWEETS_BY_HASHTAG = "hashtags/%s.out"

NUM_WINDOWS = 10
# Percent of initial outliers to prune
START_PRUNE = 0.05
END_PRUNE = 0.8

with open(sys.argv[1], 'r') as f:
    hashtags = map(lambda x: x[:-1], f.readlines())

for hashtag in hashtags:
    # Read all tweets associated with this hashtag
    with open("hashtags/%s.out" % hashtag, "rb") as f:
        tweets = pickle.load(f)

    # Partitions of users based on timestamp of tweet
    partitions = [set() for _ in xrange(NUM_WINDOWS)]

    # Set date boundaries (TODO: optimize this out)
    times = sorted([time.strptime(t.time, TIME_FORMAT) for t in tweets])
    (start_index, end_index) = len(times)*START_PRUNE, len(times)*END_PRUNE
    times = times[int(start_index):int(end_index)]

    # Determine size of time window for each partition
    start_time = time.mktime(times[0])
    end_time = time.mktime(times[-1])
    time_width = end_time - start_time + 1
    window_size = time_width / NUM_WINDOWS

    # Collect all users mentioned in relation to this hashtag and partition by time
    for t in tweets:
        # TODO: Do filtering to optimize this
        # Determine partition for this tweet
        timestamp = time.mktime(time.strptime(t.time, TIME_FORMAT))
        delta = timestamp - start_time
        if (timestamp < start_time or timestamp > end_time): continue
        index = int(delta / window_size)

        # Add nodes to that partition
        partitions[index].update(t.mentioned_entities)

    if not os.path.exists("graphs/%s" % hashtag):
       os.makedirs("graphs/%s" % hashtag)

    with open('graphs/%s/times.csv' % hashtag, 'w') as f:
        # Store the start of each partition, to be used as time labels in visualizations
        json.dump([(start_time + i*window_size) for i in xrange(NUM_WINDOWS)], f)

    # Write out user (node) lists
    for i in xrange(len(partitions)):
        with open('graphs/%s/nodes%d.csv' % (hashtag, i+1), 'w') as f:
            f.write("\n".join(sorted(partitions[i])))

    print "Wrote out node lists for ", hashtag
