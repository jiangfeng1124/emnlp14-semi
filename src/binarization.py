#!/bin/python

data = "w2v.txt"
mat = "w2v.mat" # exclude the first column (vocabulary)
cols = tuple(range(1, 51))

import sys
import numpy
print >> sys.stderr, "load embedding matrix...",
embed = numpy.loadtxt(open(mat, "r"))
print >> sys.stderr, "done."
nrow, ncol = embed.shape

p_medians = []
p_means = []
n_medians = []
n_means = []

print >> sys.stderr, "computing medians...",
for i in range(ncol):
    vec = embed[:, i]

    p_vec = vec[vec > 0]
    p_vec.sort()
    n_vec = vec[vec < 0]
    n_vec.sort()

    npos = len(p_vec)
    nneg = len(n_vec)

    p_vec_median = p_vec[npos/2]
    p_vec_mean = p_vec.mean()
    n_vec_median = n_vec[nneg/2]
    n_vec_mean = n_vec.mean()

    p_medians.append(p_vec_median)
    p_means.append(p_vec_mean)
    n_medians.append(n_vec_median)
    n_means.append(n_vec_mean)

print >> sys.stderr, "done."

words = []
f_sparsity = open("w2v.bi.sparsity", "w")
for i,l in enumerate(open(data, "r")):
    print >> sys.stderr, "\r%d" % (i),

    l = l.strip().split()
    # words.append(l[0])
    word = l[0]

    src_emb = embed[i, :]
    bi_emb = []
    n_zero = 0
    for j in range(ncol):
        val = src_emb[j]
        # if val > p_medians[j]:
        if val > p_means[j]:
            bi_emb.append("+U")
        # elif val < n_medians[j]:
        elif val < n_means[j]:
            bi_emb.append("-B")
        else:
            bi_emb.append("0")
            n_zero += 1

    # print >> f_sparsity, "%s\t%f" % (l[0], float(ncol - n_zero) / ncol)
    print >> f_sparsity, "%s\t%f" % (l[0], float(n_zero) / ncol)
    print "%s %s" % (l[0], " ".join(bi_emb))

