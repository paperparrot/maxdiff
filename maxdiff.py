__author__ = 'sebastiengenty'

import numpy as np
import pandas as pd

# This program is made to take the utilities from a MaxDiff estimation and compute the relative importances for
# the attributes tested. Input for now is .csv though also working on a .xlsx solution.


def avg_imp(utilities_file, filter_var='none', weight='none'):
    """ Actual function doing all the heavy lifting. Takes in the utility scores and filters and computes the average
    importances. Has the option of adding weights if need be.
    :param utilities_file: CSV file containing the utility scores. Top row should be labels.
    :param filter_var: CSV file containing the filter values. Each filter group should be its own variable, no overlaps
    :param weight:
    :return:
    """
    raw = pd.read_csv(utilities_file, index_col='session')
    rescaled = np.exp(raw)
    rescaled = rescaled.divide(rescaled.sum(axis=0),axis=0)

    if weight is 'none':
        rescaled = rescaled
    else:
        rescaled = rescaled*weight

    if filter_var is 'none':
        output = rescaled.means()
    else:
        filts = pd.read_csv(filter_var, index_col='session')
        data = pd.concat(rescaled, filts)
        output = data.groupby(data['filter_name'])

    return output
