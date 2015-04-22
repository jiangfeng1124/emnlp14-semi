#!/bin/python

''' Merge the clustering assignment of sofia-ml with the vocabulary
'''

# input
import sys
f_assignments = sys.argv[1]
f_vocab = sys.argv[2]

# output
# cluster = open("./word_clusters.txt", "w")

vocab = {}
assign = {}

for l in open(f_vocab, "r"):
    l = l.strip().split()
    vocab[int(l[1])] = l[0]

for l in open(f_assignments, "r"):
    l = l.strip().split()
    l = map(int, l)
    if l[0] not in assign:
        assign[l[0]] = []
    assign[l[0]].append(l[1])

for k,v in assign.items():
    for e in v:
        print "%s\t%s" % (k, vocab[e])

# cluster.close()

