import plotly.express as px
from plotly.graph_objs import Figure

from computation.data import DataSessions


def empty_fig():
    """
    Returns
    -------
    plotly.express figure (px.scatter) which is an empty graph as a placeholder
    """

    fig = px.scatter()
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    return fig


def get_token_graph(session: DataSessions) -> Figure:
    """
    Parameters
    ----------
    session:
         DataSession

    Returns
    -------
    plotly.express
        figure (px.line) which shows the token usage for each product by time
    """
    if len(session.data_pings.get_metered_days()) <= 3:
        data = session.get_token_consumption(interval="15min")
    else:
        data = session.get_token_consumption()
    fig = px.line(
        data,
        x="time",
        y=["Viewing", "DMU", "Collaboration", "total"],
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")

    return fig


def get_fpc_graph(session: DataSessions) -> Figure:
    """
    Parameters
    ----------
    session:
         DataSession

    Returns
    -------
    plotly.express
        figure (px.bar) which shows percentual token usage for each product combination
    """
    fig = px.bar(
        session.get_package_combination_percentage(), x="package_names", y="usage"
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig


def get_cas_graph(session: DataSessions) -> Figure:
    """
    Parameters
    ----------
    session:
         DataSession

    Returns
    -------
    plotly.express
        figure (px.line) which shows the number of concurrent active sessions by time
    """
    if len(session.data_pings.get_metered_days()) <= 3:
        data = session.get_cas(interval="15min")
    else:
        data = session.get_cas()
    fig = px.line(
        data,
        x="time",
        y="amount",
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")

    return fig


def get_cluster_id_comparison_graph(session: DataSessions, cluster_ids: list):
    if len(session.data_pings.get_metered_days()) <= 3:
        data = session.get_selector_comparison_data(
            cluster_ids, "cluster_id", interval="15min"
        )
    else:
        data = session.get_selector_comparison_data(cluster_ids, "cluster_id")
    fig = px.line(
        data,
        x="time",
        y=cluster_ids,
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig


def get_multi_files_graph(session: DataSessions, idents: list) -> Figure:
    """
    Parameters
    ----------
    session:
         DataSession
    idents:
        list or array containing all identifier

    Returns
    -------
    plotly.express
        figure (px.line) which shows the total token usage for each file identifier
    """
    if len(session.data_pings.get_metered_days()) <= 3:
        data = session.get_selector_comparison_data(
            idents, "identifier", interval="15min"
        )
    else:
        data = session.get_selector_comparison_data(idents, "identifier")
    fig = px.line(
        data,
        x="time",
        y=idents,
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig
