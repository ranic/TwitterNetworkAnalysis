"""
Instantiate dictionary
Instantiate heapq with max_size 200
Iterate through all files in the directory
    - For each file, iterate through all lines
    - If line starts with "Hashtag:", get the hashtags after ":"
    - For each hashtag in the list, increment its count in dict

Finally, iterate through dictionary and populate heapq
"""

from pprint import pprint as pp
import heapq, pickle, sys
from collections import defaultdict
"""
NUM_FILES = 0
K = 10000
i = 0
counts = defaultdict(int)

with open('tweets/files.txt', 'r') as f:
    files = f.readlines()

for filename in files:
    i += 1
    with open('tweets/' + filename.rstrip(), 'r') as f:
        lines = [x.strip() for x in f.readlines() if x.startswith("Hashtags:")]
    
    for line in lines:
        (_,_,tagstr) = line.partition(":")
        tags = tagstr.lower().split(" ")
        for tag in tags:
            if len(tag):
                counts[tag] += 1
 
    if (i % 1500 == 0):
        print >> sys.stderr, "%d files read." % i

#Now we have counts of all the hashtags seen. Use a PQ to get top K 
heap = []
totalSum = 0.0
for tag, count in counts.iteritems():
    totalSum += count
    heapq.heappush(heap, (count, tag))
    if (len(heap) > K):
        heapq.heappop(heap)

with open('counts.dat', 'w') as f:
    pickle.dump(counts, f)

with open('heap.dat', 'w') as f:
    pickle.dump(heap, f)
"""
K = 10000
with open('counts.dat', 'r') as f:
    counts = pickle.load(f)

heap = []
totalSum = 0.0
for tag, count in counts.iteritems():
    totalSum += count
    heapq.heappush(heap, (count, tag))
    if (len(heap) > K):
        heapq.heappop(heap)

heap = map(lambda pair: (pair[0]/totalSum, pair[1]), heap)

s = 0.0
for (v,_) in heap:
    s += v

pp("Sum: %0.4f" % s)
heap.sort()
for (v, k) in heap:
    print v, k
pp(heap)
