from typing import List

import dash_bootstrap_components as dbc
import pandas as pd

from computation.data import DataSessions, LicenseUsage
from dash import html


def get_total_amount_table(session: DataSessions):
    """
    Parameter
    ---------
    session:
         DataSession which represents the session which should be used for computation

    Returns
    -------
    dbc.Table
        Table with total token amount for each product and the total token amount
    """
    data = session.get_total_token_amount()

    return dbc.Table.from_dataframe(
        pd.DataFrame({"Package": data.index, "Tokens": data.values}), id="table"
    )


def get_package_combination_table(session: DataSessions):
    """
    Parameter
    ---------
    session:
         DataSession which represents the session which should be used for computation

    Returns
    -------
    dbc.Table
        Table with percentual token usage for each product combination
    """
    data = session.get_package_combination_percentage()
    return dbc.Table.from_dataframe(
        pd.DataFrame(
            {"Combination": data.package_names, "Usage (%)": data.usage.round(2)}
        ),
        id="table",
    )


def combine_additional(additional_list: List):
    """
    Parameter
    ---------
    additional_list:
        List of objects which should be packed into one html.Div

    Returns
    -------
    html.Div which holds all items of additional_list
    """
    return html.Div(
        additional_list, id="multi_additional", className="multi_additional"
    )


def get_cas_statistics(session: DataSessions):
    """
    Gets the data of the concurrent actives session

    Parameter
    ---------
    session:
        DataSession which represents the session which should be used for computation

    Returns
    -------
     dbc.Table:
        Table with Maximum, Mean and Mean for weekdays for the concurrent active sessions
    """
    data = session.get_cas_statistics()

    return dbc.Table.from_dataframe(data, className="table_without_head")


def get_license_usage_table(license_data: LicenseUsage):
    """
    Gets the data of the license usage

    Parameter
    ---------
    license_data:
        LicenseUsage which represent the data used for the computation

    Returns
    -------
     dbc.Table:
        Table with the number of Cache Generation per Feature and the total number of Cache Generations
    """
    data = license_data.get_license_usage_data()

    return dbc.Table.from_dataframe(
        pd.DataFrame(
            {"Loader": data.feature_name, "Cache Generations": data.resource_id}
        ),
        id="table_license",
    )
