import dash_bootstrap_components as dbc
import pandas as pd

from computation.data import DataSessions


def get_total_amount_table(session: DataSessions):
    data = session.get_total_token_amount()

    return dbc.Table.from_dataframe(
        pd.DataFrame({"Package": data.index, "Tokens": data.values}), id="table"
    )
