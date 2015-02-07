#!/usr/bin/env python

"""
A feature extractor for named eneity recognition (NER).
Modified from the original implementation of Naoaki Okazaki (2010, 2011).
"""

# Separator of field values.
separator = ' '

# Field names of the input data.
# fields = 'y w pos chk'
fields = 'w pos chk y'

de_dimension = 300
se_dimension = 3000
# se_dimension = 9

import crfutils
from numpy import zeros
import math

### if the word contains an hyphen
def get_hyp(token):
    if '-' in token:
        return "T"
    else:
        return "F"

### if the first letter is uppercase
def get_cap(token):
    if token[0].isupper():
        return "T"
    else:
        return "F"

### shape of a word. for example, "Mr.Smith" -> "UL.ULLLL".
### seems not so meaningful.
def get_shape(token):
    r = ''
    for c in token:
        if c.isupper():
            r += 'U'
        elif c.islower():
            r += 'L'
        elif c.isdigit():
            r += 'D'
        elif c in ('.', ','):
            r += '.'
        elif c in (';', ':', '?', '!'):
            r += ';'
        elif c in ('+', '-', '*', '/', '=', '|', '_'):
            r += '-'
        elif c in ('(', '{', '[', '<'):
            r += '('
        elif c in (')', '}', ']', '>'):
            r += ')'
        else:
            r += c
    return r

### remove duplicates, seems meaningless.
def degenerate(src):
    dst = ''
    for c in src:
        if not dst or dst[-1] != c:
            dst += c
    return dst

### Type feature, useful!
def get_type(token):
    T = (
        'AllUpper', 'AllDigit', 'AllSymbol',
        'AllUpperDigit', 'AllUpperSymbol', 'AllDigitSymbol',
        'AllUpperDigitSymbol',
        'InitUpper',
        'AllLetter',
        'AllAlnum',
        )
    R = set(T)
    if not token:
        return 'EMPTY'

    for i in range(len(token)):
        c = token[i]
        if c.isupper():
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllDigitSymbol')
        elif c.isdigit() or c in (',', '.'):
            R.discard('AllUpper')
            R.discard('AllSymbol')
            R.discard('AllUpperSymbol')
            R.discard('AllLetter')
        elif c.islower():
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllUpperDigit')
            R.discard('AllUpperSymbol')
            R.discard('AllDigitSymbol')
            R.discard('AllUpperDigitSymbol')
        else:
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllUpperDigit')
            R.discard('AllLetter')
            R.discard('AllAlnum')

        if i == 0 and not c.isupper():
            R.discard('InitUpper')

    for tag in T:
        if tag in R:
            return tag
    return 'NO'

### 2 digits
def get_2d(token):
    return len(token) == 2 and token.isdigit()

### 4 digits
def get_4d(token):
    return len(token) == 4 and token.isdigit()

### contains only digits and alpha
def get_da(token):
    bd = False
    ba = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c.isalpha():
            ba = True
        else:
            return False
    return bd and ba

### contains only digits and symbol-p
def get_dand(token, p):
    bd = False
    bdd = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c == p:
            bdd = True
        else:
            return False
    return bd and bdd

### all chars are neither alphabet nor digits
def get_all_other(token):
    for c in token:
        if c.isalnum():
            return False
    return True

### Cap + "."
def get_capperiod(token):
    return len(token) == 2 and token[0].isupper() and token[1] == '.'

### contains capital letter
def contains_upper(token):
    b = False
    for c in token:
        b |= c.isupper()
    return b

### contains lowercase letter
def contains_lower(token):
    b = False
    for c in token:
        b |= c.islower()
    return b

### contains alphabet
def contains_alpha(token):
    b = False
    for c in token:
        b |= c.isalpha()
    return b

### contains digit
def contains_digit(token):
    b = False
    for c in token:
        b |= c.isdigit()
    return b

### contains non-digit/alphabet
def contains_symbol(token):
    b = False
    for c in token:
        b |= ~c.isalnum()
    return b

def b(v):
    return 'yes' if v else 'no'

def bc_prefix(code, p):
    if len(code) < p:
        return "%s%s" % (code, '0'*(p-len(code)))
    else:
        return code[:p]

def observation(v, defval=''):
    # Lowercased token.
    v['wl'] = v['w'].lower()
    # Token shape.
    # v['shape'] = get_shape(v['w'])
    # Token shape degenerated.
    # v['shaped'] = degenerate(v['shape'])
    # Token type.
    v['type'] = get_type(v['w'])

    # v['hyp'] = get_hyp(v['w'])
    # v['cap'] = get_cap(v['w'])

    # Prefixes (length between one to four).
    v['p1'] = v['w'][0] if len(v['w']) >= 1 else defval
    v['p2'] = v['w'][:2] if len(v['w']) >= 2 else defval
    v['p3'] = v['w'][:3] if len(v['w']) >= 3 else defval
    v['p4'] = v['w'][:4] if len(v['w']) >= 4 else defval

    # Suffixes (length between one to four).
    v['s1'] = v['w'][-1] if len(v['w']) >= 1 else defval
    v['s2'] = v['w'][-2:] if len(v['w']) >= 2 else defval
    v['s3'] = v['w'][-3:] if len(v['w']) >= 3 else defval
    v['s4'] = v['w'][-4:] if len(v['w']) >= 4 else defval

    if 'brown' in W:
        wl = v['wl']
        if wl in cluster_brown:
            v['brown'] = cluster_brown[wl]
            for prefix in [2,4,6,8,10,12,14,16]:
                v['brown-p%d' % prefix] = bc_prefix(v['brown'], prefix)
        else:
            v['brown'] = defval
            for prefix in [2,4,6,8,10,12,14,16]:
                v['brown-p%d' % prefix] = defval
    if 'de' in W:
        # print >> sys.stderr, "append dense emb"
        emb = dense_emb[v['wl']] if v['wl'] in dense_emb else map(int, zeros(de_dimension))
        for i in xrange(de_dimension):
            name = "de%d" % (i)
            v[name] = emb[i]
    if 'se' in W:
        # print >> sys.stderr, "append dense emb"
        emb = sparse_emb[v['wl']] if v['wl'] in sparse_emb else map(int, zeros(se_dimension))
        for i in xrange(se_dimension):
            name = "se%d" % (i)
            v[name] = emb[i]
    if 'ce500' in W: ## ce1000, ce2000 should be in
        if v['wl'] in cluster_emb:
            v['ce500'] = cluster_emb[v['wl']][0]
            v['ce1000'] = cluster_emb[v['wl']][1]
            v['ce2000'] = cluster_emb[v['wl']][2]
            v['ce1500'] = cluster_emb[v['wl']][3]
            v['ce3000'] = cluster_emb[v['wl']][4]
        else:
            v['ce500'] = defval
            v['ce1000'] = defval
            v['ce2000'] = defval
            v['ce1500'] = defval
            v['ce3000'] = defval
    if 'proto' in W:
        if v['wl'] in prototypes:
            v['proto'] = prototypes[v['wl']]
        else:
            v['proto'] = []
    if 'bi' in W:
        biemb = binarized_emb[v['wl']] if v['wl'] in binarized_emb else ['0']*de_dimension
        for i in xrange(de_dimension):
            name = "bi%d" % (i)
            v[name] = biemb[i]

def disjunctive(X, t, field, begin, end):
    name = '%s[%d..%d]' % (field, begin, end)
    for offset in range(begin, end+1):
        p = t + offset
        if p not in range(0, len(X)):
            continue
        X[t]['F'].append('%s=%s' % (name, X[p][field]))

U = [
    'w', 'pos', 'chk', 'type',
    'p1', 'p2', 'p3', 'p4',
    's1', 's2', 's3', 's4',
    ]
W = [] #'de', 'ce', 'proto', 'bi'
B = ['w', 'pos', 'chk']
# O = ['hyp', 'cap']

import sys
if len(sys.argv) != 2:
    print >> sys.stderr, "Usage: python %s [emb_type]" % (sys.argv[0])
    print >> sys.stderr, "emb_type = de|ce|bi|proto|bc|none"
    sys.exit(1)

emb_type = sys.argv[1]
if emb_type == "bc":
    W.append('brown')
    W.append('brown-p2')
    W.append('brown-p4')
    W.append('brown-p6')
    W.append('brown-p8')
    W.append('brown-p10')
    W.append('brown-p12')
    W.append('brown-p14')
    W.append('brown-p16')
if emb_type == "de":
    W.append('de')
if emb_type == "se":
    W.append('se')
if emb_type == "ce":
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
if emb_type == "proto":
    W.append('proto')
    # W.append('proto1')
if emb_type == "bi": # bi-mean
    W.append('bi')
if emb_type == "bi-ce":
    W.append('bi')
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
if emb_type == "bi-proto":
    W.append('bi')
    W.append('proto')
if emb_type == "ce-proto":
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
    W.append('proto')
if emb_type == "bc-proto":
    W.append('brown')
    W.append('brown-p2')
    W.append('brown-p4')
    W.append('brown-p6')
    W.append('brown-p8')
    W.append('brown-p10')
    W.append('brown-p12')
    W.append('brown-p14')
    W.append('brown-p16')
    W.append('proto')
if emb_type == "bc-ce":
    W.append('brown')
    W.append('brown-p2')
    W.append('brown-p4')
    W.append('brown-p6')
    W.append('brown-p8')
    W.append('brown-p10')
    W.append('brown-p12')
    W.append('brown-p14')
    W.append('brown-p16')
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
if emb_type == "bc-ce-proto":
    W.append('brown')
    W.append('brown-p2')
    W.append('brown-p4')
    W.append('brown-p6')
    W.append('brown-p8')
    W.append('brown-p10')
    W.append('brown-p12')
    W.append('brown-p14')
    W.append('brown-p16')
    W.append('proto')
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
if emb_type == "bi-ce-proto":
    W.append('bi')
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
    W.append('proto')
if emb_type == "de-ce-proto":
    W.append('de')
    W.append('ce500')
    W.append('ce1000')
    W.append('ce2000')
    W.append('ce1500')
    W.append('ce3000')
    W.append('proto')

templates = []
for name in U:
    templates += [((name, i),) for i in range(-2, 3)]
for name in B:
    templates += [((name, i), (name, i+1)) for i in range(-2, 2)]
# for name in O:
#     templates += [((name, 0),)]
for name in W:
    if name == "brown":
        templates += [((name, i),) for i in range(-2, 3)]
        templates += [((name, i), (name, i+1)) for i in range(-1,1)]
        templates += [((name, -1), (name, 1))]
    elif name.startswith("brown"):
        templates += [((name, i),) for i in range(-2, 3)]
    elif name.startswith("ce"):
        templates += [((name, i),) for i in range(-2, 3)]
        templates += [((name, i), (name, i+1)) for i in range(-1,1)]
        templates += [((name, -1), (name, 1))]
    elif name == "proto":
        templates += [((name, i),) for i in range(-2, 3)]
        # templates += [((name, i), (name, i+1)) for i in range(-1,1)]
        # templates += [((name, -1), (name, 1))]
    elif name == "de":
        for i in xrange(de_dimension):
            key = "%s%d" % (name, i)
            templates += [((key, i),) for i in range(-2, 3)]
    elif name == "se":
        for i in xrange(se_dimension):
            key = "%s%d" % (name, i)
            templates += [((key, i),) for i in range(-2, 3)]
    elif name == "bi":
        for i in xrange(de_dimension):
            key = "%s%d" % (name, i)
            templates += [((key, i),) for i in range(-2, 3)]

cluster_brown = {}
cluster_emb = {}
dense_emb = {}
sparse_emb = {}
prototypes = {}
binarized_emb = {}

### load cluster-like features
### including brown cluster, and embedding cluster.
def load_cluster_brown(path, sep='\t'):
    for l in open(path, "r"):
        l = l.strip().split(sep)
        cluster_brown[l[1]] = l[0]

def load_cluster_emb(path, sep='\t'):
    for l in open(path, "r"):
        l = l.strip().split(sep)
        cluster_emb[l[1]] = l[0]

def load_compound_cluster_emb(path, sep='\t'):
    for l in open(path, "r"):
        l = l.strip().split(sep)
        cluster_emb[l[0]] = l[1:]

def load_prototypes(path, sep="\t"):
    for l in open(path, "r"):
        l = l.strip().split(sep)
        prototypes[l[0]] = l[1:]

### load embedding features
### including dense embedding and sparse embedding.
def load_dense_emb(path, sep=' '):
    # global de_dimension
    for i,l in enumerate(open(path, "r")):
        # print >> sys.stderr, "\r%d" % (i),
        l = l.strip().split(sep)
        embs = map(float, l[1:])
        # if i == 0:
        #     de_dimension = len(embs)
        embs = scale(embs, metric="normalize")
        dense_emb[l[0]] = embs
    # print >> sys.stderr

def load_sparse_emb(path, sep=' '):
    for i,l in enumerate(open(path, "r")):
        print >> sys.stderr, "\r%d" % (i),
        l = l.strip().split(sep)
        embs = map(float, l[1:])
        sparse_emb[l[0]] = embs
    print >> sys.stderr

def load_binarized_emb(path, sep=' '):
    for l in open(path, "r"):
        l = l.strip().split(sep)
        embs = l[1:]
        binarized_emb[l[0]] = embs

def scale(vec, metric="minmax"):
    if metric == "minmax":
        __max = max(vec)
        __min = min(vec)
        scaled_vec = [(e - __min)/(__max - __min) for e in vec]
    elif metric == "normalize":
        __norm = math.sqrt(sum([e**2 for e in vec]))
        scaled_vec = [(e/__norm + 1)/2 for e in vec]
    return scaled_vec

def feature_extractor(X):
    # Append observations.
    for x in X:
        observation(x)

    # Apply the feature templates.
    crfutils.apply_templates(X, templates)

    # Append disjunctive features.
    for t in range(len(X)):
        disjunctive(X, t, 'w', -4, -1)
        disjunctive(X, t, 'w', 1, 4)

    # Append BOS and EOS features.
    if X:
        X[0]['F'].append('__BOS__')
        X[-1]['F'].append('__EOS__')

binarize_dir  = "./data/binarize/"
#emb_dir       = "./data/emb-wiki/"
emb_dir       = "./data/emb-manaal"
brown_dir     = "./data/brown/"
kmcluster_dir = "./data/kmcluster/"
proto_dir     = "./data/proto/code/"

import os.path
if __name__ == '__main__':

    ### for cluster features
    emb_source = "w2v"
    n_cluster = "compound"

    ### for prototype features
    normalize = "n1"
    k = 90
    # k = 600 # for binary classification
    thresh = "0.5" # 0.5 performs the best

    if 'brown' in W:
        load_cluster_brown(os.path.join(brown_dir, "paths"))
    if 'de' in W:
        # load_dense_emb(os.path.join(emb_dir, "w2v.txt"))
        # print >> sys.stderr, "load word embeddings"
        load_dense_emb(os.path.join(emb_dir, "glove_6B_300.txt"))
    if 'se' in W:
        load_sparse_emb(os.path.join(emb_dir, "glove_300_3000_l1-1_l2_1e-5"))
        # load_sparse_emb(os.path.join(emb_dir, "sample"))
    if 'ce500' in W:
        load_compound_cluster_emb(
                os.path.join(kmcluster_dir, "ccompound.txt"))
    if 'proto' in W:
        load_prototypes(
                os.path.join(proto_dir, "k40.n1.bio.pmi.protosim"))
    if 'bi' in W:
        load_binarized_emb(
                os.path.join(binarize_dir, "w2v.bi-mean.txt"))

    crfutils.main(feature_extractor, fields=fields, sep=separator)

