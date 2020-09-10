"""Instantiate a Dash app."""
import base64
import datetime
import io
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
    # Custom HTML layout
    # dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div(
        children=[
            html.Img(src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Num%C3%A9ro_1.jpg", alt="n1", style= 'width="50" height="50"'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                # Allow multiple files to be uploaded
                multiple=False
            ),
            dcc.Input(id="hostname", value="test", type="text"),
            dcc.Input(id="installation", value="your installation", type="text"),
            html.Br(),
            html.Img(src="https://upload.wikimedia.org/wikipedia/commons/9/96/Num%C3%A9ro_2.jpg", alt="n1", style= 'width="50" height="50"'),
            html.Div(id='URI-path'),
            create_data_table(df),
            html.Div(id='output-data-upload'),
        ],
        id='dash-container'
    )
    # init_callbacks()
    @dash_app.callback(
        Output(component_id='URI-path', component_property='children'),
        [Input(component_id='hostname', component_property='value'),
        Input(component_id="installation", component_property="value")]
    )
    def update_output_div(username, instalName):
        return 'URI path: {}'.format(str(username)+"/"+str(instalName))


    def parse_contents(contents, filename, date):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(
                    io.StringIO(decoded.decode('utf-8')))
            elif 'xls' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
        except Exception as e:
            print(e)
            return html.Div([
                'There was an error processing this file.'
            ])

        return html.Div([
            html.H5(filename),
            html.H6(datetime.datetime.fromtimestamp(date)),

            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.columns]
            ),

            html.Hr(),  # horizontal line

            # For debugging, display the raw contents provided by the web browser
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...', style={
                'whiteSpace': 'pre-wrap',
                'wordBreak': 'break-all'
            })
        ])
    @dash_app.callback(Output('database-table', 'children'),
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'),
            State('upload-data', 'last_modified')])

    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            children = [
                parse_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            return children

    dash_app.config.suppress_callback_exceptions = True
    dash_app.config.update({
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
        page_size=10
    )
    return table

