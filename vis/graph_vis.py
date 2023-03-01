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
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")

    return fig


def get_token_graph(session: DataSessions, graph_type: str) -> Figure:
    """
    Parameters
    ----------
    session: DataSession
    graph_type: either "bar" or "line"

    Returns
    -------
    plotly.express
        figure (px.line) which shows the token usage for each product by time
    """
    if session.get_amount_of_days() <= 3:
        data = session.get_token_consumption(interval="15min")
    else:
        data = session.get_token_consumption()

    if graph_type == "bar":
        fig = px.bar(
            data,
            x="time",
            y=["Viewing", "DMU", "Collaboration", "total"],
        )
    else:
        fig = px.line(
            data,
            x="time",
            y=["Viewing", "DMU", "Collaboration", "total"],
            render_mode="webgl",
        )

    fig.update_layout(xaxis_title="Time", yaxis_title="Token", legend_title="Products")

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
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", xaxis_title="Products", yaxis_title="Usage (%)"
    )
    return fig


def get_cas_graph(session: DataSessions, graph_type: str) -> Figure:
    """
    Parameters
    ----------
    session: DataSession
    graph_type: either "bar" or "line"

    Returns
    -------
    plotly.express
        figure (px.line) which shows the number of concurrent active sessions by time
    """
    if session.get_amount_of_days() <= 3:
        data = session.get_cas(interval="15min")
    else:
        data = session.get_cas()

    if graph_type == "bar":
        fig = px.bar(
            data,
            x="time",
            y="amount",
        )
    else:
        fig = px.line(
            data,
            x="time",
            y="amount",
            render_mode="webgl",
        )

    fig.update_layout(xaxis_title="Time", yaxis_title="CAS")

    return fig


def get_token_cluster_id_comparison_graph(
    session: DataSessions, cluster_ids: list, multi_cluster=False
):
    """
    Parameters
    ----------
    session: DataSession
    cluster_ids: list or array containing all cluster ids
    multi_cluster: bool
        True if cluster_id should be aggregated over all file identifier

    Returns
    -------
    plotly.express
        figure (px.line) which shows the total token usage for each file identifier
    """
    if session.get_amount_of_days() <= 3:
        data = session.get_selector_comparison_data(
            cluster_ids, "cluster_id", interval="15min", multi_cluster=multi_cluster
        )
    else:
        data = session.get_selector_comparison_data(
            cluster_ids, "cluster_id", multi_cluster=multi_cluster
        )

    fig = px.line(
        data,
        x="time",
        y=cluster_ids,
        render_mode="webgl",
    )
    fig.update_layout(
        xaxis_title="Time", yaxis_title="Token", legend_title="Cluster-IDs"
    )
    return fig


def get_cas_cluster_id_comparison_graph(
    session: DataSessions, cluster_ids: list, multi_cluster=False
):
    """
    Parameters
    ----------
    session: DataSession
    cluster_ids: list or array containing all cluster ids
    multi_cluster: bool
        True if cluster_id should be aggregated over all file identifier

    Returns
    -------
    plotly.express
        figure (px.line) which shows the total token usage for each file identifier
    """
    if session.get_amount_of_days() <= 3:
        data = session.get_multi_cas(
            cluster_ids, "cluster_id", interval="15min", multi_cluster=multi_cluster
        )
    else:
        data = session.get_multi_cas(
            cluster_ids, "cluster_id", multi_cluster=multi_cluster
        )

    fig = px.line(
        data,
        x="time",
        y=cluster_ids,
        render_mode="webgl",
    )
    fig.update_layout(xaxis_title="Time", yaxis_title="CAS", legend_title="Cluster-IDs")
    return fig


def get_multi_files_graph(
    session: DataSessions, idents: list, graph_type: str
) -> Figure:
    """
    Parameters
    ----------
    session: DataSession
    idents: list or array containing all identifier
    graph_type: either "bar" or "line"

    Returns
    -------
    plotly.express
        figure (px.line) which shows the total token usage for each file identifier
    """
    if session.get_amount_of_days() <= 3:
        data = session.get_selector_comparison_data(
            idents, "identifier", interval="15min"
        )
    else:
        data = session.get_selector_comparison_data(idents, "identifier")

    if graph_type == "bar":
        fig = px.bar(
            data,
            x="time",
            y=idents,
        )
    else:
        fig = px.line(
            data,
            x="time",
            y=idents,
            render_mode="webgl",
        )

    fig.update_layout(
        xaxis_title="Time", yaxis_title="Token", legend_title="Identifier"
    )

    return fig


def get_multi_cas_graph(session: DataSessions, idents) -> Figure:
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
    if session.get_amount_of_days() <= 3:
        data = session.get_multi_cas(idents, "identifier", interval="15min")
    else:
        data = session.get_multi_cas(idents, "identifier")
    fig = px.line(
        data,
        x="time",
        y=idents,
        render_mode="webgl",
    )

    fig.update_layout(xaxis_title="Time", yaxis_title="CAS", legend_title="Identifier")

    return fig
