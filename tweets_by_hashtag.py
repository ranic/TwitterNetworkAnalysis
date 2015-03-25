""" tweets_by_hashtag.py

    Input: A file containing a list of hashtags
    Output: hashtags/<hashtag>.out for each hashtag containing a list of all tweets corresponding to that hashtag
"""    
from collections import defaultdict
from Tweet import Tweet
import sys
import pickle
import time

MAX_CACHE_SIZE = 500000

with open('tweets/files.txt', 'r') as f:
    data_files = map(lambda x: x.strip(), f.readlines())

with open(sys.argv[1], 'r') as f:
    hashtags = set(map(lambda x: x.strip(), f.readlines()))

def flush_cache(cache):
    print >> sys.stderr, "Flushing cache..."
    for hashtag, tweets in cache.iteritems():
        with open("hashtags/%s.out" % hashtag, 'a') as f:
            f.write(pickle.dumps(tweets))
        
    cache.clear()

print >> sys.stderr, hashtags
cache = defaultdict(list)
cache_size = 0

k = 0
for filename in data_files:
    if (cache_size > MAX_CACHE_SIZE):
        flush_cache(cache)
        cache_size = 0

    with open("tweets/%s" % filename, 'r') as f:
        lines = map(lambda x: x.strip(), f.readlines())

    i = 0
    while ((i+9) < len(lines)):
        line = lines[i]
        if (line.startswith("Type:")):
            t = Tweet(lines[i:i+10], filename)
            for hashtag in getattr(t, 'hashtags', []):
                if (hashtag in hashtags):
                    cache[hashtag].append(t)
                    cache_size += 1
            i += 10
        i += 1

    k += 1
    if ((k % 2000) == 0):
        print "Read %d files" % k

flush_cache(cache)
