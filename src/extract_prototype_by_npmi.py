#!/bin/python

'''
This script count the PMI(tag, word),
    and select the top-k word for each tag.

PMI(tag, word) = ln(P(word, tag) / P(word) * P(tag))
P(word, tag) = C(word, tag) / N
P(word) = C(word) / N
P(tag) = C(tag) / N

Normalized_PMI_1(tag, word) = PMI(tag, word) / -ln(P(word, tag)
Normalized_PMI_2(tag, word) = ln(P(word, tag)^2 / P(word) * P(tag))
'''

from convert_bio import Corpus
import operator
import sys
import math

debug=False

def load_emb_vcb(path):
    vocab = {}
    for l in open(path):
        l = l.strip()
        vocab[l] = 1
    return vocab

if __name__ == '__main__':

    vocab = load_emb_vcb("embed.vcb")

    ne_corpus = Corpus(sys.argv[1])
    k = int(sys.argv[2]) # k prototypes

    pmi = {} # {tag: {word: pmi(tag, word)}}
    normalized_pmi_1 = {}
    normalized_pmi_2 = {}

    tag_count = {}
    word_count = {}
    tag_word_count = {} # {tag: {word : count(tag, word)}}

    N = 0
    for sent in ne_corpus.get_sent():
        nword = len(sent)
        N += nword
        for i in range(nword):
            word = sent[i][0]
            tag = sent[i][3]

            ### w/o BIO
            # if tag != "O": tag = tag[2:]

            ### for NE recognization task.
            ### merge all NE types to one NE
            #if tag != "O": tag = "NE"

            tag_count[tag] = tag_count.setdefault(tag, 0) + 1
            word_count[word] = word_count.setdefault(word, 0) + 1
            tag_word_count[tag] = tag_word_count.setdefault(tag, {})
            if word.lower() not in vocab: continue
            tag_word_count[tag][word] = tag_word_count[tag].setdefault(word, 0) + 1

    for tag,tw_count in tag_word_count.items():
        assert tag in tag_count
        pmi[tag] = {}
        normalized_pmi_1[tag] = {}
        normalized_pmi_2[tag] = {}

        for word,count, in tw_count.items():
            assert word in word_count
            pmi[tag][word] = math.log(float(count * N) / (tag_count[tag] * word_count[word]))
            normalized_pmi_1[tag][word] = pmi[tag][word] / -math.log(float(count) / N)
            normalized_pmi_2[tag][word] = math.log(float(count) * float(count) / (tag_count[tag] * word_count[word]))

    #fp_result_pmi = open("k%s.bio.pmi" % (k), "w")

    """ all NE types include BIO
    """
    fp_result_normalized_pmi_1 = open("k%s.n1.bio.pmi" % (k), "w")

    """ NE / non-NE
    """
    #fp_result_normalized_pmi_1 = open("k%s.bi.pmi" % (k), "w")
    #fp_result_normalized_pmi_2 = open("k%s.n2.bio.pmi" % (k), "w")

    for tag, tw_pmi in normalized_pmi_1.items():
        sorted_tw_pmi = sorted(tw_pmi.iteritems(), reverse=True, key=operator.itemgetter(1))
        if debug:
            proto = ["%s\t%s" % (word, val) for (word, val) in sorted_tw_pmi[:k]]
            print >> fp_result_normalized_pmi_1, "%s" % (tag)
            print >> fp_result_normalized_pmi_1, "%s" % ("\n").join(proto)
        else:
            proto = [word for (word, val) in sorted_tw_pmi[:k]]
            print >> fp_result_normalized_pmi_1, "%s\t%s" % (tag, "\t".join(proto))

