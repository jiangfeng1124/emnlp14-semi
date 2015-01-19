#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: ./tag.sh [de|bi|ce|proto|baseline]"
    exit 1
fi

root_dir=data/ner/
inst_dir=$root_dir/instances/
model_dir=$root_dir/models/
model=$model_dir/$1.model

predict_dir=$root_dir/predict/
if [ ! -d $model_dir ]; then
    mkdir $model_dir
fi

dev_corpora=$data_dir/dev.$1.inst
test_corpora=$data_dir/test.$1.inst

dev_predict=$predict_dir/dev.$1.predict
test_predict=$predict_dir/test.$1.predict

echo "[dev_corpora]  => "$dev_corpora
echo "[test_corpora] => "$test_corpora
echo "[model]        => "$model

eval_dir=$root_dir/eval/
if [ ! -d $eval_dir ]; then
    mkdir $eval_dir
fi

echo "[EXECUTE]:     => crfsuite tag -m $model -r $test_corpora > $test_predict"
crfsuite tag -m $model -r $test_corpora > $test_predict
gold_test=$root_dir/eng.test
paste $gold_test $test_predict > $eval_dir/dev.$1.eval"
sed -i 's/^\t//g' $eval_dir/dev.$1.eval"

echo "----Performance(Test)----"
perl example/conlleval.pl -d "\t" < $eval_dir/dev.$1.eval"

