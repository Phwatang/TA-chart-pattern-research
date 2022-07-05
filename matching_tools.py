# Functions to help with importing/processing and pattern matching of
# timeseries data.

# Note to self: Make sure all operations applied to series/dataframes are
#               vectorised operations. Only do a for loop if the world
#               is ending.
# %%
from typing import Union
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def data_import(f_path: str, timestamp_header: str, data_header: str) -> pd.Series:
    """Reads a file path leading to a csv and returns a Series with the
    index as a DatetimeIndex.
    ---
    Parameters:
    param f_path: File path pointing to a csv
    timestamp_header: The header of the column containing the time information
    data_header: The header of the column containing the value information"""

    data: pd.DataFrame = pd.read_csv(
        f_path, 
        usecols = [timestamp_header,data_header],
        index_col = timestamp_header).squeeze("columns")
    data.index = pd.DatetimeIndex(data.index)
    # ensure the DatetimeIndex conversion went well
    if type(data.index) != pd.DatetimeIndex:
        raise Exception("Timestamp column failed to convert to a DatetimeIndex")
    return data


def rolling_window(series: pd.Series, window_len: int) -> pd.DataFrame:
    """Returns a Dataframe consisting of rolling window segments over the underlying
    series. Index of the Dataframe is set to use the index of the series.
    ---
    E.g a length 2 rolling window over the series:

    |    Index   | Data |
    |------------|------|
    | 2020-01-01 |   13 |
    | 2020-01-02 |   16 |
    | 2020-01-03 |   19 |
    | 2020-01-04 |   21 |

    Returns the Dataframe:

    |    Index   | Col 0 | Col 1 |
    |------------|-------|-------|
    | 2020-01-01 |    13 |    16 |
    | 2020-01-02 |    16 |    19 |
    | 2020-01-03 |    19 |    21 |
    ---
    Parameters:
    series: The Series to perform the rolling window over
    window_len: The size of the window view"""

    np_array = np.lib.stride_tricks.sliding_window_view(series.to_numpy(), window_len)
    return pd.DataFrame(np_array, index=series.index[:len(np_array)])

def apply_log(series: pd.Series) -> pd.Series:
    """Returns a copy of a series with natural log applied to all the values.
    
    ---
    Parameters:
    series: The Series to be passed in"""

    return pd.Series(np.log(series.to_numpy()), index=series.index)

def horizontal_scale(vals: np.ndarray, scale: tuple[int, int]) -> np.ndarray:
    """Returns a copy of a passed in array of x values scaled according to scale
    specified. Scaling applied will ensure the plot of the output will graphically
    look exactly the same as the plot of the input.

    Scaling occurs based of the number of \"segments\" rather than the number of
    values.
    ---
    E.g

    vals = 1D array of 12 values
    
    scale = (1, 3)
    
    In this scenario, vals has 11 segments and the scale selected would cause a
    3x increase. This would cause the output array to have 22 segments and thus
    23 values.
    ---
    Parameters:
    seq: The sequence (array) of values to be scaled. Can be 1D array or 2D array
        of the shape (n_sequences * x_values).
    scale: A tuple of two ints being (in_scale, out_scale). in_scale specifies
        the scale that seq is. out_scale refers to the scale that the output array
        should conform to. The overall scaling applied to seq will depend on the
        ratio between in_scale and out_scale.
    """

    # array passed in could be 2d thus we need the length of inner most dim
    seq_len = vals.shape[-1]
    in_scale, out_scale = scale
    # Note: interp1d appears to be slow with large arrays?
    itp = interp1d(np.linspace(0, 1, seq_len), vals, kind="linear")
    return itp(np.linspace(0, 1, ((seq_len-1)//in_scale)*out_scale + 1))

def initial_diff_match(series: pd.Series, targ_seq: np.ndarray, 
    diff_range: float = 0.0, step_scalings: list[int] = [1],) -> pd.DataFrame:
    """Attempts to find a given sequence of values within the underlying series
    using (what I call) "initial differencing".

    Initial differencing: When a sequence of values is converted to a
        sequence containing the difference between nth value and the 1st value.
        E.g [3,4,-6,5,26,1] -> [0,1,-9,2,13,-2]

    ---
    Parameters:
    series: The series to overlay the tar_seq upon
    targ_seq: The target sequence. I.e sequence of values to find within the series
    step_scalings: The \"horizontal\" scalings to be applied to targ_seq before 
        overlaying it on the series.
    """

    output = pd.DataFrame(columns = ["scale", "score"])

    # I've used for loops -_- ... Guess the world is ending now.
    for scale in step_scalings:
        # Apply scaling to targ_seq
        targ_seq_adj = horizontal_scale(targ_seq, (1, scale))
        # Apply initial differencing
        targ_seq_adj = targ_seq_adj - targ_seq_adj[0]
        # Create window views over the series
        views = rolling_window(series, len(targ_seq_adj))
        # Apply initial differencing to each view
        views = views.sub(views.iloc[:, 0], axis=0)
        # Compare the tar_seq_adj to each window view
        diff_scores = (views - targ_seq_adj)
        # Filter for acceptable difference scores
        mask = ((diff_scores>-diff_range)&(diff_scores<diff_range)).all(axis=1)
        diff_scores = diff_scores[mask]
        # Place scores into a DataFrame
        diff_scores = pd.DataFrame(
            {"scale": scale, "score": diff_scores.sum(axis=1).values},
            index = diff_scores.index)
        output = pd.concat([output, diff_scores])
    return output

def POI_afterwards(series: pd.Series, POIs: pd.DataFrame, steps_after: int) -> pd.DataFrame:
    """
    Returns a Dataframe consisting of values from series that occur after given 
    points of interest (POI).
    ---
    Parameters:
    series: The series to search through
    POIs: A DataFrame that contain POI locations/indexes. Should be obtained from
        sequence_match function.
    steps_after: Number of steps to record after each POI location. Must be >1"""

    output = pd.DataFrame(columns=[i for i in range(steps_after+1)])

    # For every POI
    for i in range(len(POIs)):
        # Get details about the POI
        point = POIs.iloc[i]
        # Get where the POI occurs in the series
        ind = series.index.get_loc(point.name)
        # Retrieve values that occur after the POI
        after = series[ind : ind+1+steps_after]
        # Convert to dataframe and format to append to output
        after = after.to_frame().T
        after.columns = [i for i in range(after.shape[-1])]
        after.index = [point.name]
        output = pd.concat([output, after])
    return output

def purge_date_repeats(data: Union[pd.Series, pd.DataFrame]) -> pd.Series:
    """Takes in a series containing a DatetimeIndex and removes rows that occur
    on the same date (except for the first occurance).
    ---
    Parameters:
    series: The Pandas Series to perform the purging on
    """

    if len(data) == 0:
        return data
    
    dates = data.index.date
    mask = ~pd.Series(dates).duplicated(keep="first").to_numpy()
    return data[mask]
# %%
