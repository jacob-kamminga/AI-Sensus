import pandas as pd
import os

from data_export import windowing as w


def export(data: [], label_col: str, timestamp_col: str, file_path: str, comments: [str], comment=';'):
    """
    Exports a list of DataFrames after using the windowing_fast method to get a statistical
    overview of the data contained in the DataFrames. The DataFrames are required to have
    a column for labels and a column for timestamps. All other columns will be used for
    windowing.
    :param data: The DataFrames that are exported.
    :param label_col: The column containing the labels.
    :param timestamp_col: The column containing the timestamps.
    :param file_path: The path of the newly created file.
    :param comments: A list of comments that will be added at the head of the file.
    :param comment: The style used to denote comments (defaults to ';')
    :return:
    """
    # Initialise result list
    res = []

    # Get list of columns to be windowed over
    collist = data[0].columns.tolist()
    collist.remove(label_col)
    collist.remove(timestamp_col)

    # Window over data per DataFrame
    for df in data:
        new_df = w.windowing_fast(df, collist, label_col, timestamp_col)
        res.append(new_df)

    # Turn list into one DataFrame
    df = pd.concat(res)

    # Remove file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write comments to a file and use that as start file for 'to_csv'
    f = open(file_path, 'a')
    for c in comments:
        f.write(comment + c + '\n')

    # Write DataFrame to the file
    df.to_csv(f)

    # Close the file
    f.close()
