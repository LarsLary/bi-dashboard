import dash_bootstrap_components as dbc
import dash_uploader

from dash import dash, dcc, html
from vis.graph_vis import empty_fig


def header() -> html.Header:
    """
    Returns
    -------
    html.Header which describes the header of the Feature Usage Tab
    """

    head = html.Header(
        [
            html.Div(
                [
                    html.Button(
                        [
                            html.Img(
                                src="assets/settings-icon.svg",
                                height="43px",
                                className="settings-icon",
                            )
                        ],
                        className="settings-button",
                        id="open-settings-button",
                    )
                ],
                className="col-2",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dash_uploader.Upload(
                                text="Upload Report",
                                text_completed="Upload Report. Latest: ",
                                id="dash-uploader",
                                filetypes=["csv"],
                            )
                        ]
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(
                                dbc.ModalTitle("Please enter a file identifier")
                            ),
                            dbc.ModalBody(
                                dbc.Input(
                                    id="ident",
                                    placeholder="identifier",
                                    type="text",
                                    debounce=True,
                                    className="input",
                                )
                            ),
                            dbc.ModalFooter(
                                html.Button("Confirm", id="confirm", className="button")
                            ),
                        ],
                        id="modal_ident",
                        is_open=False,
                    ),
                ],
                className="col-2 center",
            ),
            html.Div(
                [
                    "Time interval: ",
                    dcc.DatePickerRange(
                        id="select-date",
                        month_format="MMMM Y",
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
                        style={"verticalAlign": "top", "margin-right": "15px"},
                    )
                ],
                className="col-2 logo",
            ),
        ],
        className="header",
        id="header",
    )

    return head


DROPDOWN_OPTIONS = [
    {"label": "Token Consumption", "value": 0},
    {"label": "Concurrent Active Sessions", "value": 1},
    {"label": "Product Usage", "value": 2},
    {"label": "Cluster-ID Comparison", "value": 3},
    {"label": "File Comparison (Token)", "value": 4},
    {"label": "File Comparison (CAS)", "value": 5},
]


def body_feature():
    """
    Returns
    -------
    html.Div which represents the html body of the dashboard tab Feature Usage Frontend
    """

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [],
                        className="left-column",
                    ),
                    html.Div(  # content: graphs + data
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            DROPDOWN_OPTIONS,
                                            value=0,
                                            id="dropdown1",
                                            className="dropdown",
                                            clearable=False,
                                        )
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            DROPDOWN_OPTIONS,
                                            value=1,
                                            id="dropdown2",
                                            className="dropdown",
                                            clearable=False,
                                        )
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            dcc.Graph(figure=empty_fig()),
                                            id="graph1",
                                            className="graph",
                                        )
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            dcc.Graph(figure=empty_fig()),
                                            id="graph2",
                                            className="graph",
                                        )
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            "",
                                            id="graph_data1",
                                            className="graph_data",
                                        )
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            "",
                                            id="graph_data2",
                                            className="graph_data",
                                        )
                                    ),
                                ],
                            ),
                        ],
                        className="content",
                        id="content",
                    ),
                ],
                id="main",
                className="main",
            ),
        ]
    )


def tab_layout():
    """
    Returns
    -------
    html.Div which represents the html body of the complete dashboard Frontend
    """

    return html.Div(
        [
            header(),
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="Feature Usage",
                        children=body_feature(),
                        className="tab-right",
                        id="tab1",
                    ),
                    dcc.Tab(
                        label="Transcoder Usage",
                        children=body_license(),
                        className="tab-left",
                        id="tab2",
                    ),
                    dcc.Tab(
                        label="File Statistics",
                        children=[
                            dbc.Table(
                                overview_table,
                                className="table-statistics",
                                id="file-data-table",
                            )
                        ],
                        className="tab-middle",
                        id="tab3",
                    ),
                ],
                id="tabs",
            ),
            pop_up_messages(),
            stores(),
        ]
    )


def body_license():
    """
    Returns
    -------
    html.Div which represents the html body of the dashboard tab License Usage Frontend
    """
    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div([""], id="graph_data3", className="graph_data")),
                ]
            ),
            dcc.Store(id="filename_license", data=""),
        ]
    )


def pop_up_messages():
    """
    Returns
    -------
    html.Div which represents the html format of the pop up messages
    """
    return html.Div(
        [
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
            html.Div(
                html.Div("Database reset completed"),
                id="reset_msg",
                className="reset_msg",
            ),
            settings(),
        ]
    )


def stores():
    return html.Div(
        [
            dcc.Store(id="filename", data=""),
            html.Div(
                children=[
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                ],
                id="graphs-store",
                style={"display": "none"},
            ),
            dcc.Store(id="additionals-store", data={"0": {}, "1": {}}),
            dcc.Store(id="license-store", data={}),
        ]
    )


def settings():
    return html.Div(  # https://plotly.com/python/custom-buttons/
        [
            html.H1(["Settings"], className="settings-h1"),
            html.H2(["Graphs"], className="settings-h2"),
            html.Div(["Graph Style:"], className="text"),
            dcc.Dropdown(
                ["automatic", "bar", "line"],
                "automatic",
                id="graph-type",
                className="settings-dropdown",
                clearable=False,
            ),
            html.Div(["Select a Report:"], className="text"),
            dcc.Dropdown(
                [],
                "",
                id="file-select-feature",
                className="settings-dropdown",
                clearable=False,
            ),
            html.Div(["Select a Cluster-ID:"], className="text"),
            dcc.Dropdown(
                [],
                "",
                id="cluster_id-select",
                className="settings-dropdown",
                clearable=False,
            ),
            html.Div(["Select a license file:"], className="text"),
            dcc.Dropdown(
                [],
                "",
                id="file-select-license",
                className="settings-dropdown",
                clearable=False,
            ),
            html.H2(["Database"], className="settings-h3"),
            html.Div(["Reset:"], className="text"),
            html.Button("Reset", id="reset", className="button_reset"),
            html.Button(
                ["Close Settings"],
                id="close-settings-button",
                className="close-settings-button",
            ),
        ],
        className="settings-div",
        id="settings-div",
    )


overview_table = dash.html.Tbody(
    [
        dash.html.Tr(
            [
                dash.html.Td("Report:", className="info-table-cell"),
                dash.html.Td("", id="overview_filename", className="info-table-cell"),
            ]
        ),
        dash.html.Tr(
            [
                dash.html.Td("Lines:", className="info-table-cell"),
                dash.html.Td("", id="overview_lines", className="info-table-cell"),
            ]
        ),
        dash.html.Tr(
            [
                dash.html.Td("Calendar Days:", className="info-table-cell"),
                dash.html.Td("", id="overview_cal_days", className="info-table-cell"),
            ]
        ),
        dash.html.Tr(
            [
                dash.html.Td("Metered Days:", className="info-table-cell"),
                dash.html.Td(
                    "", id="overview_metered_days", className="info-table-cell"
                ),
            ]
        ),
    ]
)
