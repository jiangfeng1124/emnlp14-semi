#!/bin/bash

cd /export/a04/jguo/work/emnlp14-semi

root_dir=data/ner/

typ=${typ}
log_dir=$root_dir/logs/
if [ ! -d $log_dir ]; then
    mkdir $log_dir
fi

model_dir=$root_dir/models/$typ/
if [ ! -d $model_dir ]; then
    mkdir $model_dir
fi

model=$model_dir/model

train_corpora=$root_dir/eng.train.inst.$typ
dev_corpora=$root_dir/eng.dev.inst.$typ
test_corpora=$root_dir/eng.test.inst.$typ

cost=1.0

log_file=$log_dir/$typ.log
crfsuite learn -m $model -p feature.possible_states=1 -p feature.possible_transitions=1 -a l2sgd -p c2=$cost -e2 $train_corpora $dev_corpora

#> $log_file 2>&1
