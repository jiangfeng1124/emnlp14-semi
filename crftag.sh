#!/bin/bash

root_dir=data/ner/

typ=$1

model_dir=$root_dir/models/$typ/
model=$model_dir/model

dev_corpora=$root_dir/eng.dev.inst.$typ
test_corpora=$root_dir/eng.test.inst.$typ

predict_dir=$root_dir/predict/
if [ ! -d $predict_dir ]; then
    mkdir $predict_dir
fi
dev_predict=$predict_dir/dev.$typ.predict
test_predict=$predict_dir/test.$typ.predict

eval_dir=$root_dir/eval/
if [ ! -d $eval_dir ]; then
    mkdir $eval_dir
fi

echo "[EXECUTE]:     => crfsuite tag -m $model -r $test_corpora > $test_predict"
crfsuite tag -m $model -r $test_corpora > $test_predict
gold_test=$root_dir/eng.test
paste $gold_test $test_predict > $eval_dir/test.$typ.eval
sed -i 's/^\t//g' $eval_dir/test.$typ.eval

echo "----Performance(Test)----"
perl src/conlleval.pl -d "\t" < $eval_dir/test.$1.eval

