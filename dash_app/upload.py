import os
from time import sleep
from typing import Callable

import pandas as pd
from dash import dash

import database.driver as driver
from computation.data import DataPings, DataSessions
from computation.features import Features
from dash_app import background

UPLOAD_CACHE_PATH = os.path.abspath("./cache/upload_data/")


def convert_report_to_df(name: str):
    """
    Parameters
    ----------
    name : String
        the name of a csv-file

    Returns
    -------
    pd.Dataframe which represents the csv-file
    """
    return pd.read_csv(UPLOAD_CACHE_PATH + "/" + name)


def prepare_license_data(
    set_progress: Callable, header_text: str, datagram: pd.DataFrame, filename: str
):
    """
    Prepare data of license file after upload of a license file

    Parameter
    ---------
    set_progress : Callable
        progress bar
    header_text : str
        header text of progress bar
    datagram : pd.DataFrame
        data of file
    filename : str
        identifier of file
    """

    """Step 2: Skipped"""

    """Step 3: Skipped"""

    """Step 4: Set identifier Type as "Licence" in database"""
    set_progress((60, "3/5", header_text, "Loading License Data", False))
    sleep(1)
    background.set_type_of_last_identifier("License")

    """Step 5: Store license data in database"""
    license_data = datagram
    ident = background.get_last_identifier()
    license_data["identifier"] = ident
    driver.df_to_sql_append(datagram, "license")
    set_progress((100, "5/5", header_text, "Loaded Data Successfully", False))
    sleep(1)

    return None, False, dash.no_update, filename


def prepare_feature_data(
    set_progress: Callable, header_text: str, datagram: pd.DataFrame, filename: str
):
    """
    Prepare data of feature file after upload of a feature file

    Parameter
    ---------
    set_progress : Callable
        progress bar
    header_text : str
        header text of progress bar
    datagram : pd.DataFrame
        data of file
    filename : str
        identifier of file
    """

    set_progress((20, "1/5", header_text, "Getting Features", False))
    sleep(1)

    """Step 2: Get Features"""
    features = Features().get_data_features()
    set_progress((40, "2/5", header_text, "Extracting Pings", False))
    sleep(1)

    """Step 3: Create DataPings object"""
    data_pings = DataPings(filename, datagram, features)
    set_progress((60, "3/5", header_text, "Prepare Extracting DataSessions", False))

    """Step 4: Create DataSessions object"""
    data_session = DataSessions(pd.DataFrame([]), data_pings, features, 300, "")
    set_progress((80, "4/5", header_text, "Extracting Session Blocks", False))

    """Step 5: Extract sessions"""
    data_session.extract_session_blocks()

    df_session = data_session.data.copy()
    df_pings = data_pings.data.copy()

    """Set identifier Type as "Feature" in database"""
    background.set_type_of_last_identifier("Feature")

    """Add identifier to data in database"""
    ident = background.get_last_identifier()
    df_session["identifier"] = ident
    df_pings["identifier"] = ident

    """Store feature data in database"""
    driver.df_to_sql_append(df_session, "session")
    driver.filter_duplicates("session")

    driver.df_to_sql_append(df_pings, "pings")
    driver.filter_duplicates("pings")

    """Store cluster_ids in database"""
    cluster_ids = data_session.get_cluster_ids()
    cluster_ids = cluster_ids.to_frame()
    cluster_ids["identifier"] = ident
    driver.df_to_sql_append(cluster_ids, "cluster_ids")

    """Get rid of previous data"""
    driver.drop_current_table()
    set_progress((100, "5/5", header_text, "Loaded Data Successfully", False))

    return None, False, filename, dash.no_update
