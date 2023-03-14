import os
from time import sleep
from typing import Callable

import pandas as pd
from dash import dash

import database.driver as driver
from computation.data import DataPings, DataSessions
from computation.features import Features
from computation.file_imports import upload_csv, upload_zip
from csv_config import feature_map, license_map

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
    set_progress: Callable, datagrams: list, filename: str, ident_num: int, ident_names
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

        ident_name = ident_names[len(ident_names) - (1 + ident_num)]

        header_text = "Uploading " + name
        set_progress((0, "0/5", header_text, "Converting Data", False, ""))
        sleep(0.5)

        if license_map["grant_id"] in datagram.columns:
            set_progress((60, "3/5", header_text, "Loading License Data", False, ""))
            sleep(0.5)
            datagram = rename_columns(datagram, license_map)

            table = driver.get_df_from_db("identifier")
            if (
                table.loc[table["FileIdentifier"] == ident_name, "Type"].item()
                == "unknown"
            ):
                table.loc[table["FileIdentifier"] == ident_name, "Type"] = "License"
            else:
                table.loc[
                    table["FileIdentifier"] == ident_name, "Type"
                ] = "Feature, License"
            ident = ident_name
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
            datagram = rename_columns(datagram, feature_map)

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
            if (
                table.loc[table["FileIdentifier"] == ident_name, "Type"].item()
                == "unknown"
            ):
                table.loc[table["FileIdentifier"] == ident_name, "Type"] = "Feature"
            else:
                table.loc[
                    table["FileIdentifier"] == ident_name, "Type"
                ] = "Feature, License"

            ident = ident_name
            driver.df_to_sql_replace(table, "identifier")

            df_session["identifier"] = ident
            df_pings["identifier"] = ident

            driver.df_to_sql_append(df_session, "session")
            driver.filter_duplicates("session")

            driver.df_to_sql_append(df_pings, "pings")
            driver.filter_duplicates("pings")

            # Calculate and save report statistics
            report_statistics(data_pings, ident_name)

            # Calculate and save ClusterID statistics
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


def report_statistics(data_pings: DataPings, ident_name: str):
    """
    Calculate and save report statistics

    Parameters
    ----------
    data_pings : DataPings
        DataPings of the uploaded file
    ident_name : str
        Identifier of the uploaded file
    """

    # Calculate and save report statistics
    if driver.check_if_table_exists("report_statistics"):
        report_statistics = driver.get_df_from_db("report_statistics")
    else:
        report_statistics = pd.DataFrame(
            columns=["Report", "Lines", "Total Days", "Earliest Day", "Last Day"]
        )
    report_statistics.set_index("Report", inplace=True)

    # Calculate statistics
    lines = f"{len(data_pings.get_pings().index):,}".replace(",", " ")
    sequence_of_days = data_pings.get_sequence_of_days()
    total_days = str(len(sequence_of_days))
    earliest_cal_day = str(sequence_of_days[0])
    last_cal_day = str(sequence_of_days[-1])

    # Append or update statistics in report_statistics
    if ident_name in report_statistics.index:
        report_statistics.loc[ident_name, "Lines"] = lines
        report_statistics.loc[ident_name, "Total Days"] = total_days
        report_statistics.loc[ident_name, "Earliest Day"] = earliest_cal_day
        report_statistics.loc[ident_name, "Last Day"] = last_cal_day
    else:
        report_statistics.loc[ident_name] = [
            lines,
            total_days,
            earliest_cal_day,
            last_cal_day,
        ]

    # Save report_statistics
    report_statistics.reset_index(inplace=True)
    driver.df_to_sql_replace(report_statistics, "report_statistics")


def rename_columns(df: pd.DataFrame, column_names_map: dict):
    """
    Rename columns of a dataframe according to the feature map

    Parameters
    ----------
    df : pd.DataFrame
        dataframe to rename
    column_names_map : dict
        map of old column names to new column names

    Returns
    -------
    pd.DataFrame with renamed columns
    """
    for new_name, old_name in column_names_map.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    return df
