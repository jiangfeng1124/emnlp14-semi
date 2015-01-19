#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: ./train.sh [de|bi|ce|proto|baseline]"
    exit 1
fi

root_dir=data/ner/
inst_dir=$root_dir/instances/
if [ ! -d $inst_dir ]; then
    mkdir $inst_dir
fi
model_dir=$root_dir/models/$1/
if [ ! -d $model_dir ]; then
    mkdir $model_dir
fi

train_corpora=$inst_dir/train.$1.inst
dev_corpora=$inst_dir/dev.$1.inst
test_corpora=$inst_dir/test.$1.inst

echo "collect training instances"
python src/enner.py $1 < $root_dir/eng.train > $train_corpora
python src/enner.py $1 < $root_dir/eng.dev   > $dev_corpora
python src/enner.py $1 < $root_dir/eng.test  > $test_corpora

# for each setting, we have tuned the cost (l2 coef) to an optimal value
#   on the development dataset
if [ "$1" == "de" ]; then
    cost=0.4
elif [ "$1" == "de" ]; then
    cost=0.2
elif [ "$1" == "bi" ]; then
    cost=0.4
elif [ "$1" == "ce" ]; then
    cost=0.1
elif [ "$1" == "proto" ]; then
    cost=0.2
elif [ "$1" == "ce-proto" ]; then # combination
    cost=1.0
elif [ "$1" == "bc-ce-proto" ]; then
    cost=1.9
else
    echo "Usage: ./train.sh [de|bi|ce|proto]"
    exit 1
fi

model=$model_dir/$1.model

echo "[train_corpora] ==> "$train_corpora
echo "[model] ==> "$model
echo "EXECUTE: crfsuite learn -m $model -p feature.possible_states=1 -p feature.possible_transitions=1 -a l2sgd -p c2=$cost -e2 $train_corpora $dev_corpora"

log_dir=$root_dir/logs/
if [ ! -d $log_dir ]; then
    mkdir $log_dir
fi
log_file=$log_dir/$1.log"
crfsuite learn -m $model -p feature.possible_states=1 -p feature.possible_transitions=1 -a l2sgd -p c2=$cost -e2 $train_corpora $dev_corpora > $log_file 2>&1

