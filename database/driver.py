import os
import sqlite3
from sqlite3 import Connection

import pandas as pd
import sqlalchemy

connection: Connection = None
PATH = os.path.abspath("./cache/data_table.db")


def create_con() -> Connection:
    """
    Creates a connection to the database
    with the path specified in PATH

    Returns
    -------
    Connection:
        the connection to the database
    """
    global connection
    con = sqlite3.connect(PATH, check_same_thread=False)
    connection = con
    return con


def close_con() -> None:
    """
    Closes the current open connection to the database
    """
    connection.close()


def df_to_sql_append(df: pd.DataFrame, name: str) -> None:
    """
    Appends the dataframe to the current database table

    Parameters
    ----------
    df: pd.Dataframe
        the data to be appended
    name: String
        the name of the table
    """
    create_con()
    df.to_sql(name=name, con=connection, if_exists="append", index=False)
    close_con()


def df_to_sql_replace(df: pd.DataFrame, name: str) -> None:
    """
    Replaces the current database table with the dataframe

    Parameters
    ----------
    df: pd.Dataframe
            the new data
    name: String
        the name of the table
    """
    create_con()
    df.to_sql(name=name, con=connection, if_exists="replace", index=False)
    close_con()


def drop_all() -> None:
    """
    Drops all existing tables
    """
    cursor = create_con().cursor()

    cursor.execute("drop table if exists pings")
    cursor.execute("drop table if exists session")
    cursor.execute("drop table if exists license")
    cursor.execute("drop table if exists identifier")
    cursor.execute("drop table if exists cluster_ids")
    cursor.execute("drop table if exists report_statistics")

    close_con()

    drop_current_table()


def drop_current_table() -> None:
    """
    Drops the current_data table
    """
    cursor = create_con().cursor()
    cursor.execute("drop table if exists current_data")
    close_con()


def get_engine() -> sqlalchemy.engine.Engine:
    """
    Returns
    -------
    sqlalchemy.engine:
        the engine to the database with the path specified in PATH
    """
    return sqlalchemy.create_engine(
        "sqlite:///" + PATH, execution_options={"sqlite_raw_colnames": True}
    )


def check_if_table_exists(table_name: str) -> bool:
    """
    checks if a table exists
    Parameter
    ---------
    table_name: String
        the name of the table

    Returns
    -------
    True if the table exits, False if the table does not exist
    """
    cursor = create_con().cursor()
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,)
    )
    ret = bool(tables.fetchone())
    close_con()
    return ret


def get_df_from_db(table_name: str) -> pd.DataFrame:
    """
    Gets a dataframe out of a database table

    Parameter
    ---------
    table_name: String
        the name of the table

    Returns
    -------
    pd.Dataframe:
        the data of the database table
    """
    create_con()
    df = pd.read_sql_table(table_name, get_engine())
    close_con()
    return df


def filter_duplicates(table_name: str, identifier=None):
    """
    Filters all duplicates in a database table

    Parameter
    ---------
    table_name: String
        the name of the table
    identifier: list
        a subset of the table which should be used to filter the duplicates
    """

    df = get_df_from_db(table_name)
    if identifier is None:
        identifier = df.columns
    df = df.drop_duplicates(subset=identifier, ignore_index=True, keep="last")
    df_to_sql_replace(df, table_name)


def get_last_input(table_name: str):
    """
    Gets the latest input of a datatable

    Parameter
    ---------
    table_name: String
        the name of the table

    Returns
    -------
    String
        last input in a datatable
    """
    cursor = create_con().cursor()
    last = cursor.execute(
        "SELECT * FROM " + table_name + " ORDER BY ROWID DESC LIMIT 1"
    ).fetchall()

    close_con()
    return last[0][0]
