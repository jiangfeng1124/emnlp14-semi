#!/bin/bash

### This program clusters word embeddings into $n$ clusters, using the sofia-ml tookit.
### Should install sofia-ml (https://code.google.com/p/sofia-ml/) first.

if [ $# -ne 3 ]; then
    echo "Usage: ./emb_kmeans.sh [embfile] [n_class] [dim]"
    exit 1
fi

orig_emb=$1
n_class=$2
dim=$3

work_dir=$orig_emb"-"$n_class

if [ ! -d $work_dir ]; then
    mkdir $work_dir
fi

init_type=optimized_kmeans_pp

conv_emb=$orig_emb.kmf
vocab=$orig_emb.vcb
model=$work_dir/$init_type.kmm
assignment=$work_dir/$init_type.asg

result=$work_dir/$init_type.kmc

# convert original word embedding of the following format:
#   word 0.12 0.45 ....
# into two separate files: the embedding matrix ($conv_emb), and vocabulary ($vocab)

# sofia-ml will take $conv_emb as training data.
# The clustering results will be post-processed to merge with $vocab using scripts/merge.py

if [ ! -f $conv_emb ] || [ ! -f $vocab ]; then
    python scripts/convert.py $orig_emb > $conv_emb 2>$vocab
fi

# train
# ./sofia-kmeans --k $n_class --init_type $init_type --opt_type mini_batch_kmeans --mini_batch_size 10 --iterations 10000 --objective_after_init --objective_after_training --training_file $conv_emb --model_out $model --dimensionality 300
./sofia-kmeans --k $n_class \
               --init_type $init_type \
               --opt_type mini_batch_kmeans \
               --mini_batch_size 300 \
               --iterations 200000 \
               --objective_after_init \
               --objective_after_training \
               --training_file $conv_emb \
               --model_out $model \
               --dimensionality $dim #--random_seed 10

# predict
./sofia-kmeans --model_in $model --test_file $conv_emb --objective_on_test --cluster_assignments_out $assignment

# merge results
python scripts/merge.py $assignment $vocab > $result

