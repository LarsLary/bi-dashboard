import base64
import io
import os
import sys
import webbrowser
from datetime import date
from threading import Thread
from time import sleep
from typing import Callable

import dash_bootstrap_components as dbc
import diskcache
import pandas as pd

from computation.data import DataPings, DataSessions
from computation.features import Features
from dash import Dash, Input, Output, State, ctx, dash, dcc
from dash.long_callback import DiskcacheLongCallbackManager
from vis.additional_data_vis import (
    get_cas_statistics,
    get_package_combination_table,
    get_total_amount_table,
)
from vis.graph_vis import empty_fig, get_cas_graph, get_fpc_graph, get_token_graph
from vis.web_designs import tab_layout

GRAPH_LINE_COLOR = "#edf0f1"

# Diskcache - needed for long_callbacks
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

# Dash
app = Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    long_callback_manager=long_callback_manager,
)
app.title = "Token Dashboard Threedy"
app._favicon = "threedy_favicon.png"
app.layout = dbc.Container(tab_layout(), fluid=True)


def convert_report_to_df(data):
    """
    Parameters
    ----------
    data : byte-data of a csv-file

    Returns
    -------
    pd.Dataframe which represents the csv-file
    """
    try:
        return pd.read_csv(
            io.StringIO(base64.b64decode(data.split(",")[1]).decode("utf-8"))
        )
    except Exception as e:  # TODO: catch this exception more precise
        print(e)  # TODO: Notify user that an exception occured (maybe via Popup)


def select_graph(menu_entry: str, session: DataSessions):
    """
    Parameters
    ----------
    menu_entry : String which defines the selected graph
    session : pd.Dataframe which represents the datapoints used for the selected graph

    Returns
    -------
    plotly.express figure which is a selected graphical representation of the dataframe
    dbc.Table : A table which represents additional information to the graph
    """
    fig = empty_fig()
    additional = ""
    if menu_entry == "Token Consumption":
        fig = get_token_graph(session)
        additional = get_total_amount_table(session)
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Token",
            legend_title="Products",
        )
    elif menu_entry == "Product Usage":
        fig = get_fpc_graph(session)
        fig.update_layout(xaxis_title="Products", yaxis_title="Usage (%)")
        additional = get_package_combination_table(session)
    elif menu_entry == "Concurrent Active Sessions":
        fig = get_cas_graph(session)
        fig.update_layout(xaxis_title="Time", yaxis_title="CAS")
        additional = get_cas_statistics(session)

    fig.update_traces(hovertemplate=None, hoverinfo="skip")

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
    )

    return fig, additional


def select_date(sel_date, df: pd.DataFrame, asc: bool, init_change: bool):
    """
    Parameters
    ----------
    sel_date : String which represents a date, selected in the calendar tool
    df : pd.Dataframe used to extract a date out of this dataframe
    asc : boolean which is true if the date should be the beginning date and
            false if the date should be the ending date
    init_change : boolean which is true if a new date should be loaded out of the dataframe

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


@app.callback(
    Output(component_id="file-data-table", component_property="children"),
    Output(component_id="graph1", component_property="children"),
    Output(component_id="graph2", component_property="children"),
    Output(component_id="graph_data1", component_property="children"),
    Output(component_id="graph_data2", component_property="children"),
    Output("select-date", "start_date"),
    Output("select-date", "end_date"),
    Output("current-data", "data"),
    Input(component_id="dropdown1", component_property="value"),
    Input(component_id="dropdown2", component_property="value"),
    Input("select-date", "start_date"),
    Input("select-date", "end_date"),
    Input("data-store", "data"),
    Input("current-data", "data"),
    Input("pings", "data"),
    Input("filename", "data"),
    prevent_inital_call=True,
)
def update_output_div(
    drop1: str,
    drop2: str,
    start_date: str,
    end_date: str,
    data: dict,
    current_data: dict,
    pings: dict,
    filename: str,
):
    """
    Parameters
    ----------
    drop1 : String which represents the selected entry in the dropdown menu with the id 'dropdown1'
    drop2 : String which represents the selected entry in the dropdown menu with the id 'dropdown2'
    start_date : String which represents the selected entry of the beginning day in the calendar tool
                    with the id 'select-date'
    end_date : String which represents the selected entry of the ending day in the calendar tool
                    with the id 'select-date'
    data : dict which represents the dataframe extracted out of the loaded csv-file
    current_data : dict which represents the dataframe stored in the memory
    pings : dict which represents the dataframe containing all the pings
    filename : str which is the name of the file from which the pings come from

    main computation of the frontend

    Returns
    -------
    String which the number of days inbetween the selected days of the calendar tool
            or the first and last day of the dataframe
    String which represents the metered days in the dataframe
    dcc.Graph which represents the graph with the id 'graph1'
    dcc.Graph which represents the graph with the id 'graph2'
    String which represents additional data to the graph with the id 'graph1'
    String which represents additional data to the graph with the id 'graph2'
    date.Date which represents the first selected day in the calendar tool
    date.Date which represents the last selected day in the calendar tool
    dict which represents a trimmed version of the complete dataframe
    """
    if data is not None:
        features = Features().get_data_features()

        """computation if the data is loaded first or the selected date is changed"""
        if ctx.triggered_id == "data-store" or ctx.triggered_id == "select-date":
            """converting the dict containing all data back into a pd.Dataframe"""
            df = pd.DataFrame.from_dict(data)

            """converting Strings representing date into data.Date dates"""
            data_pings = DataPings(filename, pd.DataFrame.from_dict(pings), features)
            sessions = DataSessions(df, data_pings, features, 300)

            """checking if new data is loaded and new inital dates should be set"""
            new_data = False
            if ctx.triggered_id == "data-store":
                new_data = True
            """setting the first and last dates for the represented data"""
            last = select_date(end_date, sessions.data, False, new_data)
            first = select_date(start_date, sessions.data, True, new_data)

            """trimming the dataframe to fit into the selected dates"""
            sessions.crop_data(first, last)

            """creating the both graphs based on the chosen entry in the dropdown menu"""
            fig1, additional1 = select_graph(drop1, sessions)
            fig2, additional2 = select_graph(drop2, sessions)

            return (
                get_overview_table(sessions.data_pings),
                dcc.Graph(figure=fig1, className="graph"),
                dcc.Graph(figure=fig2, className="graph"),
                additional1,
                additional2,
                first,
                last,
                sessions.data.to_dict(),
            )

        """converting the dict containing all data back into a pd.Dataframe"""
        df_current = pd.DataFrame.from_dict(current_data)

        data_pings = DataPings(filename, pd.DataFrame.from_dict(pings), features)
        sessions = DataSessions(df_current, data_pings, features, 300)

        """computation if a different representation of graph1 is selected"""
        if ctx.triggered_id == "dropdown1":
            """creating graph1 based on the chosen entry in the dropdown menu"""
            fig1, additional1 = select_graph(drop1, sessions)

            return (
                dash.no_update,
                dcc.Graph(figure=fig1, className="graph"),
                dash.no_update,
                additional1,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

        """computation if a different representation of graph2 is selected"""
        if ctx.triggered_id == "dropdown2":
            """creating graph2 based on the chosen entry in the dropdown menu"""
            fig2, additional2 = select_graph(drop2, sessions)

            return (
                dash.no_update,
                dash.no_update,
                dcc.Graph(figure=fig2, className="graph"),
                dash.no_update,
                additional2,
                dash.no_update,
                dash.no_update,
                dash.no_update,
            )

    return (
        get_overview_table(None),
        dcc.Graph(figure=empty_fig()),
        dcc.Graph(figure=empty_fig()),
        "",
        "",
        start_date,
        end_date,
        dash.no_update,
    )


def get_overview_table(data_pings: DataPings) -> dash.html.Tbody:
    """
    Creates an html table that contains some key metrics for given DataPings

    Parameters
    ----------
    data_pings : DataPings which represents the selected entry in the dropdown menu with the id 'dropdown1'

    Returns
    -------
    dash.html.Tbody containing 4 rows: report, lines, calendar days and metered days
    """
    if data_pings is not None:
        filename = str(data_pings.get_filename())
        lines = str(len(data_pings.get_pings().index))
        cal_days = str(len(data_pings.get_sequence_of_days()))
        metered_days = str(len(data_pings.get_metered_days()))
    else:
        filename = ""
        lines = ""
        cal_days = ""
        metered_days = ""

    return dash.html.Tbody(
        [
            dash.html.Tr(
                [
                    dash.html.Td("Report:", className="info-table-cell"),
                    dash.html.Td(filename, className="info-table-cell"),
                ]
            ),
            dash.html.Tr(
                [
                    dash.html.Td("Lines:", className="info-table-cell"),
                    dash.html.Td(lines, className="info-table-cell"),
                ]
            ),
            dash.html.Tr(
                [
                    dash.html.Td("Calendar Days:", className="info-table-cell"),
                    dash.html.Td(cal_days, className="info-table-cell"),
                ]
            ),
            dash.html.Tr(
                [
                    dash.html.Td("Metered Days:", className="info-table-cell"),
                    dash.html.Td(metered_days, className="info-table-cell"),
                ]
            ),
        ]
    )


@app.long_callback(
    output=[
        Output(component_id="data-store", component_property="data"),
        Output(component_id="pings", component_property="data"),
        Output(component_id="filename", component_property="data"),
    ],
    inputs=[
        Input(component_id="upload", component_property="contents"),
        State("upload", "filename"),
    ],
    running=[
        (Output("main", "style"), {"filter": "grayscale(100%)"}, {}),
        (Output("header", "style"), {"filter": "grayscale(100%)"}, {}),
        (
            Output("progress_div", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
    progress=[
        Output("progress_bar", "value"),
        Output("progress_bar", "label"),
        Output("progress_bar_header", "children"),
        Output("progress_message", "children"),
    ],
    prevent_inital_call=True,
)
def load_data(set_progress: Callable, data: str, name: str):
    """
    Parameters
    ----------
    set_progress : Function to update the website while this callback function is running
    data : Bytestream of data which represents the uploaded csv-file
    name : String which represents the filename of the loaded csv-file

    Returns
    -------
    int which represents the number of lines in the csv-file
    String which represents the filename of the loaded csv-file
    dict containing the extracted data sessions data out of the csv-file
    dict containing the extracted data pings data out of the csv-file
    """
    if data is not None:
        header_text = "Upload Report"
        set_progress((0, "0/4", header_text, "Converting Data and Extracting Features"))
        # without "sleep()" the user cannot see the first progress on the website
        sleep(1)

        # 1. Convert Data
        filename = name.split(".")[0]
        datagram = convert_report_to_df(data)
        features = Features().get_data_features()
        set_progress((25, "1/4", header_text, "Extracting DataPings"))

        # 2. Extract DataPings
        data_pings = DataPings(filename, datagram, features)
        set_progress((50, "2/4", header_text, "Extracting DataSessions"))

        # 3. Extract DataSessions
        data_session = DataSessions(pd.DataFrame([]), data_pings, features, 300)
        set_progress((75, "3/4", header_text, "Extracting Session Blocks"))

        # 4. Extract Session Blocks
        data_session.extract_session_blocks()
        set_progress((100, "4/4", header_text, "Loaded Data Successfully"))

        return (
            data_session.data.to_dict(),
            data_pings.data.to_dict(),
            data_pings.get_filename(),
        )
    return None, None, ""


@app.callback(
    Output(component_id="exportFunc", component_property="data"),
    Input(component_id="export", component_property="n_clicks"),
    State("data-store", "data"),
    State("upload", "filename"),
    prevent_initial_call=True,
)
def export_data(clicks: int, data: dict, name: str):
    """
    Parameters
    ----------
    clicks : int which represents the number of times the 'upload' button was  clicked
    data : dict which represents the stored dataframe in the memory
    name : String which represents the filename of the loaded csv-file

    downloads the dataframe onto the users computer into a textfile

    Returns
    -------
    None
    """

    """Returns if data should be exported"""
    if clicks is not None:
        return dict(
            content=pd.DataFrame.from_dict(data).to_string(), filename=name + ".txt"
        )


def open_browser(port: int):
    """
    Parameters
    ----------
    port : int which represents a port number

    opens a browser with a specifed ip and port

    Returns
    -------
    None
    """
    sleep(1)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new(f"http://127.0.0.1:{port}/")
    sys.exit()  # Close thread


if __name__ == "__main__":
    port = 8050
    Thread(target=open_browser, args=[port]).start()
    app.run_server(
        debug=True, port=port
    )  # TODO: debug must be set to false in production
