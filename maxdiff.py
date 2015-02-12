# coding=utf-8
__author__ = 'sebastiengenty'

import numpy as np
import pandas as pd
import sys

"""
This program is made to take the utilities from a MaxDiff estimation and compute the relative importances for
the attributes tested. Input for now is .csv though also working on a .xlsx solution.
"""


def avg_imp(utilities_file, filter_var=None, weight_var=None):
    """ Actual function doing all the heavy lifting. Takes in the utility scores and filter_df and computes the average
    importances. Has the option of adding weights if need be.
    :param utilities_file: CSV file containing the utility scores. Top row should be labels.
    :param filter_var: CSV file containing the filter values. Each filter group should be its own variable, no overlaps
    :param weight_var:
    :return:
    """

    # Load the file, format data
    raw_df = pd.read_csv(utilities_file, index_col='Respondent')
    raw_df = raw_df.drop('RLH', axis=1)
    raw_df['fixed_item'] = 0

    # Exponentiate the utilities, rescale so the sum is 100 for each respondent
    rescaled_df = np.exp(raw_df)
    rescaled_df = (rescaled_df.divide(rescaled_df.sum(axis=1), axis=0)*100)

    # Taking care of the weighting scheme. Weights are loaded, applied and then discarded
    if weight_var is not None:
        weights = pd.read_csv(weight_var, index_col='session')
        rescaled_df = pd.merge(rescaled_df, weights, left_index=True, right_index=True)
        rescaled_df.apply(lambda x: np.asarray(x) * np.asarray(rescaled_df['weight']))
        rescaled_df = rescaled_df.drop('weight', axis=1)

    # If filters are needed, it adds them, and creates tables by each sub filter
    if filter_var is None:
        output_df = rescaled_df.mean()
        rescaled_output = output_df*100/(output_df.mean())
    else:
        filter_df = pd.read_csv(filter_var, index_col='session')
        data = pd.merge(rescaled_df, filter_df, left_index=True, right_index=True)

        # Loop that goes through each filter group and generates a row for each
        # Those are then added to the output_df table
        output_df = pd.DataFrame(data.mean()).transpose()
        for column in filter_df.columns:
            local_df = data.groupby(column).mean()
            local_df['filter'] = column
            # add to running total
            output_df = output_df.append(local_df, ignore_index=True)

        # Filter columns are now deleted
        for column in filter_df.columns:
            output_df = output_df.drop(column, axis=1)

        # Compute the base sizes for each of the subgroups. First we compute total, then each subgroup using a loop
        base_size = pd.Series(data.ix[:, 1].count())
        for column in filter_df.columns:
            temp_count = filter_df[column].value_counts(sort=False, ascending=2)
            temp_count = pd.DataFrame(temp_count)
            temp_count['filter'] = column
            base_size = base_size.append(temp_count)

        filter_list = pd.Series(output_df['filter'])
        output_df = output_df.drop('filter', axis=1)
        rescaled_output = output_df.divide(output_df.mean(axis=1), axis=0)*100
        rescaled_output['filter'] = filter_list
        print base_size
    
    rescaled_output = rescaled_output.transpose()
    
    return rescaled_output


def main():
    args = sys.argv
    file_name = args[1]
    filters = args[2]
    weights = args[3]
    
    avg_imp(file_name, filters, weights)

if __name__ == '__main__':
    main()
