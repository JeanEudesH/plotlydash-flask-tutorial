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
from .layout import html_layout


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
    dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div(
        children=[
            input_file(),
            resource_type(),         
            additionnal_data(),
            # create_data_table(df),
            download_uri(),
            html.Div(id='uri_output')
        ],
        id='dash-container'
    )
    init_callbacks(dash_app)    

    return dash_app.server

def init_callbacks(dash_app):
    @dash_app.callback(
        Output(component_id='URI-path', component_property='children'),
        [Input(component_id='hostname', component_property='value'),
        Input(component_id="installation", component_property="value")], method=['GET', 'POST']
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
    @dash_app.callback(Output('uri_output', 'children'),
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'),
            State('upload-data', 'last_modified')])

    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            children = [
                parse_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            return children

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

def create_select():
    ResourceType = ['actuator', 'annotation', 'data', 'ear', 'event', 'image', 'leaf', 'plant', 'plot', 'pot', 'sensor', 'species', 'vector']
    return dcc.Dropdown(
        id='resource_type',
        options= [
            {"label": i, "value": i} for i in ResourceType
        ]    
    )

def input_file():
    return html.Div(className="input_file", children=[
            html.Img(src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Num%C3%A9ro_1.jpg"),
            html.Br(),
            html.Label("Import your file"),
            html.P("A file with one row for each resource you want to generate a URI for."),
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
            )
    ])

def resource_type():
    return html.Div(className="resource_type", children=[
                html.Img(src="https://upload.wikimedia.org/wikipedia/commons/9/96/Num%C3%A9ro_2.jpg"),
                html.Br(),
                html.Label("Host Name"), html.Br(),
                dcc.Input(id="hostname", value="test", type="text"), html.Br(),
                html.Label("Installation name"), html.Br(),
                dcc.Input(id="installation", value="your installation", type="text"),
                html.Div(id='URI-path'),
                html.Br(),
                html.Label('Object Type'), html.Br(),
                create_select(),
                html.Br()
    ])

def additionnal_data():
    return  html.Div(className="additional_data", children=[
                html.Img(src="https://upload.wikimedia.org/wikipedia/commons/5/52/Num%C3%A9ro_3.jpg"),
                html.Br(),
                html.Label("Data to put in the URI"),
                html.Div(children=[
                    html.Label("Year"), html.Br(),
                    dcc.Input(id="year", type="text", value="2020")
                ]),
                html.Div(children=[
                    html.Label("Project related"), html.Br(),
                    dcc.Input(id="project", type="text", value="aProject")
                ]),
                html.Div(children=[
                    html.Label("Related plant column"), html.Br(),
                    dcc.Input(id="relPlant", type="text", value="Related_plant")
                ]),
                html.Div(children=[
                    html.Label("Species column"), html.Br(),
                    dcc.Input(id="species", type="text", value="Species")
                ])
            ])

def download_uri():
    return html.Div(children=[
        
        html.Button('Generate URI', id='generate_URI', className="btn-primary-btn" )
    ])