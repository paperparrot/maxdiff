# coding=utf-8
__author__ = 'sebastiengenty'

import numpy as np
import pandas as pd

"""
This program is made to take the utilities from a MaxDiff estimation and compute the relative importances for
the attributes tested. Input for now is .csv though also working on a .xlsx solution.
"""


def avg_imp(utilities_file, filter_var=None, weight=None):
    """ Actual function doing all the heavy lifting. Takes in the utility scores and filter_df and computes the average
    importances. Has the option of adding weights if need be.
    :param utilities_file: CSV file containing the utility scores. Top row should be labels.
    :param filter_var: CSV file containing the filter values. Each filter group should be its own variable, no overlaps
    :param weight:
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
    if weight is not None:
        weights = pd.read_csv(weight, index_col='session')
        rescaled_df = pd.concat(rescaled_df, weights)
        rescaled_df.apply(lambda x: np.asarray(x) * np.asarray(rescaled_df['weight']))
        rescaled_df = rescaled_df.drop('weight', axis=1)

    # If filters are needed, it adds them, and creates tables by each sub filter
    if filter_var is None:
        output = rescaled_df.mean()
        rescaled_output = output*100/(output.mean())
    else:
        filter_df = pd.read_csv(filter_var, index_col='session')
        data = pd.merge(rescaled_df, filter_df, left_index=True, right_index=True)

        # Loop that goes through each filter group and generates a row for each.
        # Those are then added to the output table.
        output = pd.DataFrame(data.mean()).transpose()
        for column in filter_df.columns:
            local_df = data.groupby(column).mean()
            local_df['filter'] = column
            # add to running total
            output = output.append(local_df, ignore_index=True)

        # Filter columns are now deleted

        for column in filter_df.columns:
            output = output.drop(column, axis=1)

        filt_list = pd.Series(output['filter'])
        output = output.drop('filter', axis=1)
        # rescaled_output = output.divide(output.mean(axis=1))*100
        # rescaled_output = pd.concat(rescaled_output, filt_list)
        rescaled_output = output
    return rescaled_output
