from datetime import date
from typing import Union

import pandas as pd

import database.driver as driver
from computation.data import DataPings, DataSessions
from vis.additional_data_vis import (
    get_cas_statistics,
    get_cluster_id_table,
    get_multi_total_amount_table,
    get_package_combination_table,
    get_total_amount_table,
)
from vis.graph_vis import (
    get_cas_cluster_id_comparison_graph,
    get_cas_graph,
    get_fpc_graph,
    get_multi_cas_graph,
    get_multi_files_graph,
    get_token_cluster_id_comparison_graph,
    get_token_graph,
)

HIGH_PERF_MODE = True
GRAPH_LINE_COLOR = "#FFFFFF"


def select_date(sel_date: str, df: pd.DataFrame, asc: bool, init_change: bool):
    """
    Parameters
    ----------
    sel_date : String
        represents a date, selected in the calendar tool
    df : pd.Dataframe
        used to extract a date out of this dataframe
    asc : boolean
        true if the date should be the beginning date and
        false if the date should be the ending date
    init_change : boolean
        true if a new date should be loaded out of the dataframe

    Returns
    -------
    date.Date which represents a given date
    """
    if sel_date is None or init_change:
        data = df.sort_values(
            by="block_start", ascending=asc, ignore_index=True
        ).block_start[0]
    else:
        data = sel_date
        data = data.split("T")
        data = data[0].split()
        data = data[0].split("-")
        data = date(int(data[0]), int(data[1]), int(data[2]))
    return data


def get_overview_table(
    data_pings: Union[None, DataPings],
    file_identifier: str,
    cluster_id: Union[None, str],
):
    """
    Get overview table data.

    Parameters
    ----------
    data_pings : DataPings which represents the selected entry in the dropdown menu with the id 'dropdown1'
    file_identifier: String which represents the identifier of each file
    cluster_id: String which represents the cluster_id that is selected

    Returns
    -------
    filename: str
        name of report
    lines: str
        number of pings
    cal_days: str
        number of calendar days
    metered_days: str
        number of metered days
    """
    if data_pings is not None:
        data_pings_new = DataPings(
            file_identifier,
            data_pings.data[data_pings.data["identifier"] == file_identifier],
            data_pings.features,
            cluster_id,
        )
        filename = str(data_pings_new.get_filename())
        lines = str(len(data_pings_new.get_pings().index))
        cal_days = str(len(data_pings_new.get_sequence_of_days()))
        metered_days = str(len(data_pings_new.get_metered_days()))
    else:
        filename = ""
        lines = ""
        cal_days = ""
        metered_days = ""

    return (
        filename,  # current identifier
        lines,  # current number of lines of pings
        cal_days,  # current number of selected days
        metered_days,  # current number of selected days with data
    )


def get_cluster_ids_of(identifier: str):
    """
    Return cluster ids belonging to given identifier

    Parameter
    ---------
    identifier : str

    Returns
    -------
    list of str
        list of cluster ids
    """
    c_ids = driver.get_df_from_db("cluster_ids")
    c_ids = c_ids[c_ids["identifier"] == identifier]
    return c_ids["cluster_id"].to_numpy().tolist()


def get_license_data():
    """
    Return license data belonging to given identifier

    Parameter
    ---------
    identifier : str

    Returns
    -------
    pd.DataFrame
        data frame containing license data
    """
    license_data = driver.get_df_from_db("license")
    return license_data


def get_license_identifier():
    """
    Return license identifier

    Returns
    -------
    list of str
        license identifier
    """
    idents = []
    if driver.check_if_table_exists("identifier"):
        idents = driver.get_df_from_db("identifier")
        idents = (
            idents[
                (idents["Type"] == "License") | (idents["Type"] == "Feature, License")
            ]["FileIdentifier"]
            .to_numpy(dtype=str)
            .flatten()
            .tolist()
        )
    return idents


def get_feature_identifier():
    """
    Return feature identifier

    Returns
    -------
    list of str
        feature identifier
    """
    idents = []
    if driver.check_if_table_exists("identifier"):
        idents = driver.get_df_from_db("identifier")
        idents = (
            idents[
                (idents["Type"] == "Feature") | (idents["Type"] == "Feature, License")
            ]["FileIdentifier"]
            .to_numpy(dtype=str)
            .flatten()
            .tolist()
        )
    return idents


def get_last_identifier():
    """
    Return the last identifier in database

    Returns
    -------
    str
        last identifier in database or None if database table is empty
    """
    if driver.check_if_table_exists("identifier"):
        ident = driver.get_last_input("identifier")
    else:
        ident = None
    return ident


def set_type_of_last_identifier(type_name: str):
    """
    Set the type of last identifier in database

    Parameter
    ---------
    type_name : str
    """
    table = driver.get_df_from_db("identifier")
    table.loc[len(table.index) - 1, "Type"] = type_name
    driver.df_to_sql_replace(table, "identifier")


def select_graph(
    menu_entry: str,
    session: DataSessions,
    identifier: str,
    graph_type: str,
    multi_cluster: bool,
):
    """
    Parameters
    ----------
    menu_entry : String which defines the selected graph
    session : pd.Dataframe which represents the datapoints used for the selected graph
    identifier : str which represents the identifier of the currently chosen file
    graph_type: either "bar" or "line"
    multi_cluster: bool
        True if all data should be aggregated over all files

    Returns
    -------
    plotly.express figure which is a selected graphical representation of the dataframe
    pd.DataFrame : DataFrame ready for dbc.Table component


    Raises
    ------
    Exception
        If menu_entry is not implemented
    """
    """create empty additional data field in case it isn't needed for visualisation"""
    additional = pd.DataFrame()
    idents = get_feature_identifier()

    """select graph and additional data depending on parameter menu_entry"""
    if menu_entry == "Token Consumption":
        fig = get_token_graph(session, graph_type=graph_type)
        additional = get_total_amount_table(session)

    elif menu_entry == "Product Usage":
        fig = get_fpc_graph(session)
        additional = get_package_combination_table(session)

    elif menu_entry == "Concurrent Active Sessions":
        fig = get_cas_graph(session, graph_type=graph_type)
        additional = get_cas_statistics(session)

    elif menu_entry == "Cluster-ID Comparison (Token)":
        if multi_cluster:
            c_ids = session.get_cluster_ids()
        else:
            c_ids = get_cluster_ids_of(identifier)
        c_ids = list(dict.fromkeys(c_ids))
        fig = get_token_cluster_id_comparison_graph(session, c_ids, multi_cluster)
        additional = get_cluster_id_table(session, multi_cluster)

    elif menu_entry == "Cluster-ID Comparison (CAS)":
        if multi_cluster:
            c_ids = session.get_cluster_ids()
        else:
            c_ids = get_cluster_ids_of(identifier)
        c_ids = list(dict.fromkeys(c_ids))
        fig = get_cas_cluster_id_comparison_graph(session, c_ids, multi_cluster)

    elif menu_entry == "File Comparison (Token)":
        fig = get_multi_files_graph(session, idents, graph_type=graph_type)
        additional = get_multi_total_amount_table(session, idents)

    elif menu_entry == "File Comparison (CAS)":
        fig = get_multi_cas_graph(session, idents)

    else:
        raise Exception('menu entry "', menu_entry, '" does not exist.')

    if HIGH_PERF_MODE:
        fig.update_traces(hovertemplate=None, hoverinfo="skip")

    """set graph options"""
    fig.update_xaxes(
        showline=True,
        linecolor=GRAPH_LINE_COLOR,
        gridcolor=GRAPH_LINE_COLOR,
        zerolinecolor=GRAPH_LINE_COLOR,
        zerolinewidth=1,
    )
    fig.update_yaxes(
        showline=True,
        linecolor=GRAPH_LINE_COLOR,
        gridcolor=GRAPH_LINE_COLOR,
        zerolinecolor=GRAPH_LINE_COLOR,
        zerolinewidth=1,
    )
    fig.update_layout(
        font_family="sans-serif",
        font_color=GRAPH_LINE_COLOR,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=70, r=15, t=15, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig, additional
