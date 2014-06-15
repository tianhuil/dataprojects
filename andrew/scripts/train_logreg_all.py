import sys
import numpy as np
import itertools

import delays_logreg as dl
import global_vars as gv

#Put all the predictors in a single list, as well as a key to whether they're discrete or continuous
def collect_predictors(continuous_predictors,discrete_predictors):
    all_predictors = list(continuous_predictors)
    all_predictors.extend(discrete_predictors)
    all_predictor_types = [0]*len(continuous_predictors)
    all_predictor_types.extend([1]*len(discrete_predictors))

    return all_predictors,all_predictor_types    

def permute_predictors(predictors,predictor_types):
    permuted_predictors = []
    permuted_predictor_types = []
    pred_idxs = range(len(predictors))
    for i in range(1,len(predictors)+1):
        idx_permutations = list(itertools.combinations(pred_idxs,i))
        predictor_permutations = [[predictors[itup] for itup in tup] for tup in idx_permutations]
        predictor_type_permutations = [[predictor_types[itup] for itup in tup] for tup in idx_permutations]
        permuted_predictors.extend(predictor_permutations)
        permuted_predictor_types.extend(predictor_type_permutations)
    return permuted_predictors,permuted_predictor_types
        

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("Syntax: [CSV list of continuous predictors (or 'none')] [CSV list of discrete predictors (or 'none')] ['all' to do all predictor permutations]")

    continuous_predictors = []
    if sys.argv[1].lower() != 'none':
        continuous_predictors = sys.argv[1].split(',')
    discrete_predictors = []
    if sys.argv[2].lower() != 'none':
        discrete_predictors = sys.argv[2].split(',')
    do_all_permutations = sys.argv[3]

    all_predictors,all_predictor_types = collect_predictors(continuous_predictors,discrete_predictors)

    permuted_predictors,permuted_predictor_types = permute_predictors(all_predictors,all_predictor_types)

    print len(permuted_predictors)
