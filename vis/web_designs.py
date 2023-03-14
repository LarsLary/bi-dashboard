import dash_bootstrap_components as dbc
import dash_uploader
from dash import dcc, html

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
                            ),
                        ],
                        className="settings-button",
                        title="Open the settings",
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
                                filetypes=["csv", "zip"],
                            )
                        ],
                        title="Upload a report file or zip folder",
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader(
                                dbc.ModalTitle(
                                    html.Div(
                                        [
                                            html.H1(
                                                (
                                                    "Please enter an identifier for the"
                                                    " data from this file: "
                                                ),
                                                id="modal_header",
                                                className="modal_title_text",
                                            ),
                                            html.Div(
                                                (
                                                    " This Identifier will be used to"
                                                    " distinguish or associate data"
                                                    " from different files."
                                                ),
                                            ),
                                        ]
                                    )
                                )
                            ),
                            dbc.ModalBody(
                                [
                                    dbc.Input(
                                        id="ident",
                                        placeholder="identifier",
                                        type="text",
                                        debounce=True,
                                        className="input",
                                    ),
                                    dcc.Checklist(
                                        ["Use Identifier for all files"],
                                        [],
                                        id="all_file_check",
                                    ),
                                ]
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
                    dcc.Dropdown(
                        [],
                        "",
                        id="file-select-feature",
                        className="settings-dropdown",
                        clearable=False,
                    ),
                    dcc.Dropdown(
                        [],
                        "",
                        id="cluster_id-select",
                        className="settings-dropdown",
                        clearable=False,
                    ),
                ],
                className="header_dropdowns",
            ),
            html.Div(
                [
                    "Time interval: ",
                    dcc.DatePickerRange(
                        id="select-date",
                        display_format="DD-MM-YYYY",
                        month_format="MMMM Y",
                        start_date_placeholder_text="Start",
                        end_date_placeholder_text="Ende",
                    ),
                ],
                className="time",
            ),
            html.Div(
                html.Button(
                    "<->",
                    id="time-reset",
                    className="button",
                    title="Set the time interval to max values",
                )
            ),
            html.Div(
                [
                    html.Button(
                        "Export",
                        id="export",
                        className="button",
                        title="Create a PowerPoint presentation",
                    ),
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
                        style={"verticalAlign": "top", "marginRight": "15px"},
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
    {"label": "Cluster-ID Comparison (Token)", "value": 3},
    {"label": "Cluster-ID Comparison (CAS)", "value": 4},
    {"label": "File Comparison (Token)", "value": 5},
    {"label": "File Comparison (CAS)", "value": 6},
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
                        className="tab-left",
                        id="tab1",
                    ),
                    dcc.Tab(
                        label="Transcoder Usage",
                        children=body_license(),
                        className="tab-middle",
                        id="tab2",
                    ),
                    dcc.Tab(
                        label="Report Statistics",
                        children=[body_report_statistics()],
                        className="tab-right",
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
        ]
    )


def body_report_statistics():
    """
    Returns
    -------
    html.Div which represents the html body of the dashboard tab Report Statistics
    """
    return html.Div(
        [""], id="report-statistics-table", className="vertical-center-table"
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
            dcc.Store(id="filename_license", data=""),
            html.Div(
                children=[
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                    dcc.Graph(figure=empty_fig()),
                ],
                id="graphs-store",
                style={"display": "none"},
            ),
            dcc.Store(id="additions-store", data={"0": {}, "1": {}}),
            dcc.Store(id="license-store", data={}),
            dcc.Store(id="ident_num", data=0),
            dcc.Store(id="ident_names", data=0),
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
            dcc.Checklist(
                ["Aggregate Cluster ID data"],
                [],
                id="multi_cluster",
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
