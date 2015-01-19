#Embedding Features for Semi-supervised Learning
Jiang Guo, jguo@ir.hit.edu.cn

This tool is used for semi-supervised learning of NER,
using various kinds of embedding features. This tool is
associated with (Guo et al., 2014). The proposed approaches
are shown to be much better than the direct usage of
continuous word embedding features.

###Requirements:-
1. [CRFSuite](https://github.com/chokkan/crfsuite)

###Data you need:-
1. [CoNLL-2003 NER dataset](http://www.clips.ua.ac.be/conll2003/ner/)

The original dataset should be converted to BIO-style annotation.

###Training an NER tagger
1. use continuous embedding features
```./train.sh de```

2. use binarized embedding features
```./train.sh bi```

3. use clustered embedding features
```./train.sh ce```

4. use distributional prototype features
```./train.sh proto```

###Testing
```./tag.sh [de|bi|ce|proto]```

###Reference

```
@InProceedings{guo-EtAl:2014:EMNLP2014,
  author    = {Guo, Jiang  and  Che, Wanxiang  and  Wang, Haifeng  and  Liu, Ting},
  title     = {Revisiting Embedding Features for Simple Semi-supervised Learning},
  booktitle = {Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  month     = {October},
  year      = {2014},
  address   = {Doha, Qatar},
  publisher = {Association for Computational Linguistics},
  pages     = {110--120},
  url       = {http://www.aclweb.org/anthology/D14-1012}
}
```
