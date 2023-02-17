import zipfile
from io import BytesIO

import pandas as pd


def upload_zip(path: str, filename: str):
    """
    Parameters
    ----------
    path: str
        the absolute path of the zip file
    filename: str
        the name of the zip file

    Returns
    -------
    list of tuples with a pd.Dataframe and the file names
    """
    filepath = path + "/" + filename
    df_lst = []
    with zipfile.ZipFile(filepath, mode="r") as zip_file:
        files = zip_file.namelist()[1:]
        for file in files:
            if file.split(".")[-1] == "zip":
                df_lst.extend(deep_zip(BytesIO(zip_file.read(file)), file))
            elif file.split(".")[-1] == "csv":
                data = zip_file.open(file)
                df_lst.append((pd.read_csv(data), file))
    return df_lst


def deep_zip(zipfile_data: BytesIO, name: str):
    """
    Parameters
    ----------
    zipfile_data: BytesIO
        the byte representation of a zipfile
    name: str
        the name of the zip file

    Returns
    -------
    list of tuples with a pd.Dataframe and the file names
    """
    df_lst = []
    with zipfile.ZipFile(zipfile_data) as zip_file:
        files = zip_file.namelist()
        for file in files:
            if file.split(".")[-1] == "zip":
                df_lst.extend(deep_zip(BytesIO(zip_file.read(file)), file))
            elif file.split(".")[-1] == "csv":
                data = zip_file.open(file)
                df_lst.append((pd.read_csv(data), name + "/" + file))
    return df_lst


def upload_csv(path: str, filename: str):
    """
    Parameters
    ----------
    path: str
        the absolute path of the csv file
    filename: str
        the name of the csv file

    Returns
    -------
    a tuple containing a pd.Dataframe and the file name
    """
    return [(pd.read_csv(path + "/" + filename), filename)]
