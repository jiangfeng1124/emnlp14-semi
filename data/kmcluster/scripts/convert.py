#!/bin/python

''' This script simply converts original word embedding file
    output by word2vec into two separate files
        @stdout: the embedding matrix
        @stderr: the vocabulary
'''

import fileinput

vocab = {}

id = 1
for l in fileinput.input():
    l = l.strip()
    l = l.split()

    vocab[l[0]] = id

    l[0] = str(id)
    for i in xrange(1, len(l)):
        l[i] = ":".join([str(i-1), l[i]])

    print " ".join(l)

    id += 1

import sys
for k,v in vocab.items():
    print >> sys.stderr, "%s\t%s" % (k, v)

