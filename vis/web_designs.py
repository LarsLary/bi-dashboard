import dash_bootstrap_components as dbc

from dash import dcc, html


def header_feature() -> html.Header:
    """
    Parameters
    ----------
    None

    Returns
    -------
    html.Header which describes the header of the Feature Usage Tab
    """

    header = html.Header(
        [
            html.Div(className="col-2"),
            html.Div(
                dcc.Upload("Upload Report", id="upload", className="button"),
                className="col-2 center",
            ),
            html.Div(
                [
                    "Time interval: ",
                    dcc.DatePickerRange(
                        id="select-date",
                        month_format="M-D-Y-Q",
                        start_date_placeholder_text="Start",
                        end_date_placeholder_text="Ende",
                    ),
                ],
                className="time",
            ),
            html.Div(
                [
                    html.Button("Export", id="export", className="button"),
                    dcc.Download(id="exportFunc"),
                ],
                className="col-2 center",
            ),
            html.Div(
                [
                    html.Img(
                        src="assets/threedy_logo.svg",
                        height="43 px",
                        width="auto",
                        style={"verticalAlign": "top"},
                    )
                ],
                className="col-2 logo",
            ),
        ],
        className="header",
        id="header",
    )

    return header


dropdown_list = ["Token Consumption", "Concurrent Active Sessions", "Product Usage"]


def body_feature():
    """
    Parameters
    ----------
    None

    Returns
    -------
    html.Div which represents the html body of the dashboard tab Feature Usage Frontend
    """

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    "Report: ",
                                    html.Div(
                                        "", id="reportName", className="info-text"
                                    ),
                                ],
                                className="box1",
                            ),
                            html.Div(
                                [
                                    "Lines: ",
                                    html.Div("", id="lines", className="info-text"),
                                ],
                                className="box2",
                            ),
                            html.Div(
                                [
                                    "Calender Days: ",
                                    html.Div("", id="cal_days", className="info-text"),
                                ],
                                className="box3",
                            ),
                            html.Div(
                                [
                                    "Metered Days: ",
                                    html.Div("", id="daysUsed", className="info-text"),
                                ],
                                className="box4",
                            ),
                        ],
                        className="info",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(id="graph1", className="graph")),
                            dbc.Col(html.Div(id="graph2", className="graph")),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dcc.Dropdown(
                                    dropdown_list,
                                    "Token Consumption",
                                    id="dropdown1",
                                    className="dropdown",
                                    clearable=False,
                                )
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    dropdown_list,
                                    "Concurrent Active Sessions",
                                    id="dropdown2",
                                    className="dropdown",
                                    clearable=False,
                                )
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(html.Div(id="graph_data1", className="graph_data")),
                            dbc.Col(html.Div(id="graph_data2", className="graph_data")),
                        ]
                    ),
                ],
                className="content",
                id="content",
            ),
            dcc.Store(id="data-store", data=[]),
            dcc.Store(id="current-data", data=[]),
            dcc.Store(id="pings", data=[]),
            html.Div(
                [
                    html.H1(
                        "~",
                        id="progress_bar_header",
                        className="center",
                        style={"marginBottom": "3%"},
                    ),
                    html.P(
                        "~",
                        id="progress_message",
                        className="info-text",
                    ),
                    dbc.Progress(
                        id="progress_bar",
                        striped=True,
                        color="#2817e8",
                        animated=True,
                    ),
                ],
                className="progress-div",
                id="progress_div",
            ),
        ]
    )


def tab_layout():
    """
    Parameters
    ----------
    None

    Returns
    -------
    html.Div which represents the html body of the complete dashboard Frontend
    """

    return dcc.Tabs(
        [
            dcc.Tab(
                label="Feature Usage",
                children=[header_feature(), body_feature()],
                className="tab",
            ),
            dcc.Tab(
                label="License Usage",
                children=[header_license(), body_license()],
                className="tab",
            ),
        ]
    )


def header_license() -> html.Header:
    """
    Parameters
    ----------
    None

    Returns
    -------
    html.Div which represents the html header of the dashboard tab License Usage Frontend
    """
    header = html.Header(
        [
            html.Div(
                dcc.Upload("Upload Report", id="upload_license", className="button"),
                className="col-2 center",
            )
        ]
    )

    return header


def body_license():
    """
    Parameters
    ----------
    None

    Returns
    -------
    html.Div which represents the html body of the dashboard tab License Usage Frontend
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div(id="graph_data3", className="graph_data")),
                ]
            )
        ]
    )
