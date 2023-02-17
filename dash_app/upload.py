import os
from time import sleep
from typing import Callable

import pandas as pd
from dash import dash

import database.driver as driver
from computation.data import DataPings, DataSessions
from computation.features import Features
from computation.file_imports import upload_csv, upload_zip

UPLOAD_CACHE_PATH = os.path.abspath("./cache/upload_data/")


def convert_report_to_df(name: str):
    """
    Parameters
    ----------
    name : String
        the name of a file

    Returns
    -------
    list of Tuple(pd.Dataframe, str) which represents the data combined with its name
    """
    filetype = name.split(".")[-1]
    if filetype == "zip":
        return upload_zip(UPLOAD_CACHE_PATH, name)

    if filetype == "csv":
        return upload_csv(UPLOAD_CACHE_PATH, name)


def prepare_data(
    set_progress: Callable, datagrams: list, filename: str, ident_num: int
):
    """
    Prepare data of feature file after upload of a feature file

    Parameter
    ---------
    set_progress : Callable
        progress bar
    datagrams : list of Tuple(pd.DataFrame, str)
        data of file
    filename : str
        identifier of file
    ident_num : int
        number of already added identifier

    Returns
    -------
    bool which indicates if a download is complete
    str of the new feature file identifier
    str of the new license file identifier
    """

    # 1. Convert Data
    feature_filename = dash.no_update
    license_filename = dash.no_update

    one_input = False
    if ident_num == -1:
        one_input = True

    for datagram, name in datagrams:
        if one_input:
            ident_num = 0
        else:
            ident_num = ident_num - 1

        header_text = "Uploading " + name
        set_progress((0, "0/5", header_text, "Converting Data", False, ""))
        sleep(0.5)

        if "grant_id" in datagram.columns:
            set_progress((60, "3/5", header_text, "Loading License Data", False, ""))
            sleep(0.5)

            table = driver.get_df_from_db("identifier")
            if table.loc[len(table.index) - (1 + ident_num), "Type"] == "unknown":
                table.loc[len(table.index) - (1 + ident_num), "Type"] = "License"
            else:
                table.loc[
                    len(table.index) - (1 + ident_num), "Type"
                ] = "Feature, License"
            ident = table.loc[len(table.index) - (1 + ident_num), "FileIdentifier"]
            driver.df_to_sql_replace(table, "identifier")

            license_data = datagram
            license_data["identifier"] = ident
            driver.df_to_sql_append(datagram, "license")
            set_progress(
                (100, "5/5", header_text, "Loaded Data Successfully", False, "")
            )
            sleep(0.5)
            license_filename = filename
        else:
            set_progress(
                (
                    20,
                    "1/5",
                    header_text,
                    "Getting Number of Lines and Features",
                    False,
                    "",
                )
            )
            sleep(0.5)

            # 2. Get Features
            features = Features().get_data_features()
            set_progress((40, "2/5", header_text, "Extracting DataPings", False, ""))
            sleep(0.5)

            # 3. Extract DataPings
            data_pings = DataPings(filename, datagram, features)
            set_progress((60, "3/5", header_text, "Extracting DataSessions", False, ""))
            sleep(0.5)

            # 4. Extract DataSessions
            data_session = DataSessions(pd.DataFrame([]), data_pings, features, 300, "")
            set_progress(
                (80, "4/5", header_text, "Extracting Session Blocks", False, "")
            )

            # 5. Extract Session Blocks
            data_session.extract_session_blocks()

            df_session = data_session.data.copy()
            df_pings = data_pings.data.copy()

            table = driver.get_df_from_db("identifier").copy()
            if table.loc[len(table.index) - (1 + ident_num), "Type"] == "unknown":
                table.loc[len(table.index) - (1 + ident_num), "Type"] = "Feature"
            else:
                table.loc[
                    len(table.index) - (1 + ident_num), "Type"
                ] = "Feature, License"

            ident = table.loc[len(table.index) - (1 + ident_num), "FileIdentifier"]
            driver.df_to_sql_replace(table, "identifier")

            df_session["identifier"] = ident
            df_pings["identifier"] = ident

            driver.df_to_sql_append(df_session, "session")
            driver.filter_duplicates("session")

            driver.df_to_sql_append(df_pings, "pings")
            driver.filter_duplicates("pings")

            cluster_ids = data_session.get_cluster_ids()
            cluster_ids = cluster_ids.to_frame()
            cluster_ids["identifier"] = ident
            driver.df_to_sql_append(cluster_ids, "cluster_ids")

            driver.drop_current_table()
            set_progress(
                (100, "5/5", header_text, "Loaded Data Successfully", False, "")
            )
            sleep(0.5)
            feature_filename = filename

    return False, feature_filename, license_filename
