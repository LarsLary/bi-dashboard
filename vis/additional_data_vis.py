import dash_bootstrap_components as dbc
import pandas as pd

from computation.data import DataSessions


def get_total_amount_table(session: DataSessions):
    data = session.get_total_token_amount()

    return dbc.Table.from_dataframe(
        pd.DataFrame({"Package": data.index, "Tokens": data.values}), id="table"
    )


def get_cas_statistics(session: DataSessions):
    """
    Gets the data of the concurrent actives session

    Returns
    -------
     dbc.Table:
        Table with Maximum, Mean and Mean for weekdays for the concurrent active sessions
    """
    data = session.get_cas_statistics()

    return dbc.Table.from_dataframe(data, className="table_without_head")
