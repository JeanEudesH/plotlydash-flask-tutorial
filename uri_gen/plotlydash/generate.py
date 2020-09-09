"""Instantiate a Dash app."""
import numpy as np
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from .data import create_dataframe
from .import_layout import html_layout


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/import_dataset/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato'
        ]
    )

    # Load DataFrame
    df = create_dataframe()
    @app.callback(
    Output(component_id='URI-path', component_property='children'),
    [Input(component_id='hostname', component_property='value'),
     Input(component_id="installation", component_property="value")], method=['GET', 'POST']
    )
    @app.callback(Output('database-table', 'children'),
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'),
            State('upload-data', 'last_modified')])

    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div(
        children=[
            html.Div(id='URI-path'),
            create_data_table(df)
        ],
        id='dash-container'
    )
    app.config.suppress_callback_exceptions = True
    app.config.update({
    # as the proxy server will remove the prefix
    'routes_pathname_prefix': ''

    # the front-end will prefix this string to the requests
    # that are made to the proxy server
    , 'requests_pathname_prefix': ''
    })
    return dash_app.server


def create_data_table(df):
    """Create Dash datatable from Pandas DataFrame."""
    table = dash_table.DataTable(
        id='database-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        sort_action="native",
        sort_mode='native',
        page_size=100
    )
    return table

