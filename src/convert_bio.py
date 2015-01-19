#!/bin/python

'''
convert the original corpus to formal BIO-style annotation.
'''

import sys

class Corpus(object):
    def __init__(self, path):
        self.fp = open(path, "r")

    def get_sent(self):
        sent = []
        for l in self.fp:
            l = l.strip()
            if l == "":
                yield sent
                sent = []
            else:
                l = l.split()
                sent.append(l)

NE_COL = 3
CHK_COL = 2

if __name__ == '__main__':
    ne_corpus = Corpus(sys.argv[1])

    if sys.argv[2] == "chk":
        mod_col = CHK_COL
    elif sys.argv[2] == "ne":
        mod_col = NE_COL

    # reader = ne_corpus.get_sent()
    for sent in ne_corpus.get_sent():
        nword = len(sent)
        print >> sys.stderr, nword

        n_tags = []
        for i in range(nword):
            tag = sent[i][mod_col]
            if i > 0:
                last_tag = sent[i-1][mod_col]
            else:
                last_tag = "O"

            if tag.startswith("I-"):
                if last_tag == "O" or last_tag != tag:
                    n_tags.append(tag.replace("I-", "B-"))
                    continue

            n_tags.append(tag)

        assert len(n_tags) == nword
        for i in range(nword):
            sent[i][mod_col] = n_tags[i]
            print "%s" % (" ".join(sent[i]))

        print
