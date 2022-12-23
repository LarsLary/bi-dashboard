import plotly.express as px

from computation.data import DataSessions


def empty_fig():
    """
    Parameters
    ----------
    None

    Returns
    -------
    plotly.express figure (px.scatter) which is an empty graph as a placeholder
    """

    fig = px.scatter()
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    return fig


def get_token_graph(session: DataSessions):
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
    fig = px.line(
        session.get_data_with_daily_token_cost(),
        x="date",
        y=["Viewing", "DMU", "Collaboration", "XR", "ModelTracking", "total"],
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")

    return fig


def get_fpc_graph(session: DataSessions):
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


def get_cas_graph(session: DataSessions):
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
    fig = px.line(
        session.get_cas(),
        x="date",
        y="num",
        render_mode="webgl",
    ).update_layout(paper_bgcolor="rgba(0,0,0,0)")

    return fig
