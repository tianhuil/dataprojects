import sys
import os
import numpy as np
import itertools

import flightfuncs as ff
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
    if len(sys.argv) != 6:
        sys.exit("Syntax: [CSV list of continuous predictors (or 'none')] [CSV list of discrete predictors (or 'none')] [target] ['all' to do all predictor permutations] [overwrite 'yes'/'no']")

    subset = None
    timesplit = [15,45]
    C_vals = [0.1,10,1000,100000]
        
    continuous_predictors = []
    if sys.argv[1].lower() != 'none':
        continuous_predictors = sys.argv[1].split(',')
    discrete_predictors = []
    if sys.argv[2].lower() != 'none':
        discrete_predictors = sys.argv[2].split(',')
    target = sys.argv[3]
    do_all_permutations = sys.argv[4].lower()
    overwrite = sys.argv[5].lower()

    all_predictors,all_predictor_types = collect_predictors(continuous_predictors,discrete_predictors)

    #Get the required permutations of the predictors:
    permuted_predictors = [list(all_predictors)]
    permuted_predictor_types = [list(all_predictor_types)]
    if do_all_permutations == 'all':
        permuted_predictors,permuted_predictor_types = permute_predictors(all_predictors,all_predictor_types)

    #print permuted_predictors

    #Iterate through all combinations of permutations and shards:
    for i,monthkey in enumerate(gv.months.keys()):
        for j,hourkey in enumerate(gv.hours.keys()):
            tablename = 'flightdelays_{month}_{hour}'.format(month=monthkey,hour=hourkey)
            for k,predictors in enumerate(permuted_predictors):
                #Get the predictors in order:
                predictors = np.array(predictors)
                predictor_types = np.array(permuted_predictor_types[k])
                c_preds = predictors[predictor_types == 0]
                d_preds = predictors[predictor_types == 1]

                #Create a pickle filename based on the predictors and month/hour:
                # filename = "../saved_models/{table}_{preds}.pkl".format(table=tablename,preds='-'.join(np.sort(predictors)).replace('(','~').replace(')','~'))
                filename = ff.make_model_pickle_filename(tablename,predictors,dir_structure="../saved_models/")

                #Test if pickle file exists already:
                file_exists = os.path.isfile(filename)
                print filename,file_exists
                #sys.exit(1)
                if overwrite == 'yes' or file_exists == False:
                    dl.train_log(tablename,continuous_predictors=list(c_preds),discrete_predictors=list(d_preds),targetname=target,subset=subset,timesplit=timesplit,filename=filename,C_vals=C_vals)
            #sys.exit(1)
