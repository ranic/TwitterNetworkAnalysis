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
SIMPLE_DATE_FORMAT = "%m-%d-%y"
TWEETS_BY_HASHTAG = "hashtags/%s.out"

with open(sys.argv[1], 'r') as f:
    hashtags = map(lambda x: x[:-1], f.readlines())

for hashtag in hashtags:
    # Read all tweets associated with this hashtag
    with open("hashtags/%s.out" % hashtag, "rb") as f:
        tweets = pickle.load(f)

    # Users that tweeted hashtag before FIRST_DATE
    first_users = set()
    # Before SECOND_DATE 
    second_users = set()
    # Before THIRD_DATE 
    third_users = set()

    # Set date boundaries
    times = [time.strptime(t.time, TIME_FORMAT) for t in tweets]
    times.sort()

    FIRST_DATE = times[len(times)/3]
    SECOND_DATE = times[2*len(times)/3]
    THIRD_DATE = times[-1]

    # Collect all users mentioned in relation to this hashtag
    for t in tweets:
        timestamp = time.strptime(t.time, TIME_FORMAT)

        if (timestamp > SECOND_DATE):
            third_users.update(t.mentioned_entities)
        elif (timestamp > FIRST_DATE):
            second_users.update(t.mentioned_entities)
        else:
            first_users.update(t.mentioned_entities)

    # Make the sets cumulative
    second_users.update(first_users)
    third_users.update(second_users)

    if not os.path.exists("graphs/%s" % hashtag):
       os.makedirs("graphs/%s" % hashtag)

    with open('graphs/%s/times.csv' % hashtag, 'w') as f:
        json.dump(map(lambda x: time.strftime(SIMPLE_DATE_FORMAT, x), [FIRST_DATE, SECOND_DATE, THIRD_DATE]), f)

    # Write out user (node) lists
    with open('graphs/%s/nodes1.csv' % hashtag, 'w') as f:
        f.write("\n".join(sorted(first_users)))

    with open('graphs/%s/nodes2.csv' % hashtag, 'w') as f:
        f.write("\n".join(sorted(second_users)))

    with open('graphs/%s/nodes3.csv' % hashtag, 'w') as f:
        f.write("\n".join(sorted(third_users)))

    print "Wrote out node lists for ", hashtag
