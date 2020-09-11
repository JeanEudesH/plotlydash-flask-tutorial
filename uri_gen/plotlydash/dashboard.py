"""Instantiate a Dash app."""
import base64
import datetime
import io
import os
import numpy as np
import pandas as pd
import hashlib
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from flask import flash
from .data import create_dataframe
from .layout import html_layout
from ..routes import User, user_collected_URI, session, db, dir_path

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
                html.H1("Generate new URI"),
                input_file(),
                details(),
                resource_type(),         
                additionnal_data(),
                # create_data_table(df),
                download_uri(),
            # html.Div(id='table_output'),
            html.A(href="uploads/exportURI.csv", download="export_URI", children=["Download"]),
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
        Input(component_id="installation", component_property="value")]
    )
    def update_output_div(username, instalName):
        return 'URI path: {}'.format(str(username)+"/"+str(instalName))

    @dash_app.callback(Output('table_output', 'children'),
            [Input('upload-data', 'contents')],
            [State('upload-data', 'filename'),
             State('upload-data', 'last_modified')])
    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            children = [
                parse_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            return children

    @dash_app.callback(Output('uri_output', 'children'),
    [Input(component_id='generate_URI', component_property='n_clicks')],
    [State(component_id='hostname', component_property='value'),
    State(component_id='installation', component_property='value'),
    State(component_id='sep', component_property='value'),
    State(component_id='skiprows', component_property='value'),
    State(component_id='species', component_property='value'),
    State(component_id='year', component_property='value'),
    State(component_id='project', component_property='value'),
    State(component_id='relPlant', component_property='value'),
    State(component_id='resource_type', component_property='value'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')]
    )
    def import_dataset(btn_activate, hostname, installation, sep, skiprows, species, year, project, relPlant, resource_type, contents, filename):
        if btn_activate>0:
            dataset = parse_data(contents, filename)
            # file.save(os.path.join(dir_path ,'uploads','uploaded_file.csv'))
            # try:
            #   dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
            # except pd.errors.EmptyDataError:
            #   flash("Invalid file, did you submit a csv file ?")
            #   return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
            # dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)

            if resource_type in ['leaf', 'ear']:
                try:
                    dataset.eval(relPlant)
                except pd.core.computation.ops.UndefinedVariableError:
                    flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")

                dataset_URI = add_URI_col(data=dataset, host = hostname, installation=installation, resource_type = resource_type , project = project, year = year, datasup = relplant)
            
            if resource_type == "species":
                try:
                    dataset.eval(species)
                except pd.core.computation.ops.UndefinedVariableError:
                    flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
                dataset_URI = add_URI_col(data=dataset, host = hostname, installation=installation, resource_type = resource_type, datasup = species)  
            
            if resource_type in ['plant', 'pot', 'plot']:
                dataset_URI = add_URI_col(data=dataset, host = hostname, installation=installation, resource_type = resource_type, project = project, year = year)
            
            if resource_type in ['sensor', 'vector', 'data', 'image', 'event', 'annotation','actuator']:
                dataset_URI = add_URI_col(data=dataset, host = hostname, installation=installation, resource_type = resource_type , year = year)
            
            dataset_URI.to_csv(os.path.join(dir_path,'uploads','export_URI.csv'))
            # send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI'+resource_type +'.csv'), mimetype="text/csv", as_attachment=True)
            return dash_table.DataTable(
                        data=dataset_URI.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in dataset_URI.columns],
                        page_size=10
            )
    
    # def read_data(list_of_contents, list_of_names):
    #     children = [
    #         parse_data(list_of_contents, list_of_names)
    #     ]
    #     return children
             
    def parse_data(contents, filename):
        content_type, content_string = contents[0].split(',')
        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename[0]:
                # Assume that the user uploaded a CSV file
                # ici des arguments pour skiprow et sep
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
        return  df

    

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
            html.Img(src="https://upload.wikimedia.org/wikipedia/commons/d/d1/Num%C3%A9ro_1.jpg", className="steps"),
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
                multiple=True
            )
    ])

def details():
    return html.Div(id="Details", children=[
        html.P("Details"),
        html.I(className="arrow down"),
        html.Label("Field separator"), html.Br(),
        dcc.Checklist(id="sep", 
            value=[',', '\\t'],
            labelStyle={'display': 'inline-block'},
            options=[
                { 'label': 'Comma (,)', 'value': ','}, 
                { 'label': 'Semicolon (;)', 'value': ';'}, 
                { 'label': 'Tabulation (\\t)', 'value': '\\t'}
            ]),
        html.Br(),
        html.Label("Number of rows to skip (no data, but comments in the first __ rows)"),
        dcc.Input(type="text", id="skiprows", value=0), html.Br()
    ])

def resource_type():
    return html.Div(className="resource_type", children=[
                html.Img(src="https://upload.wikimedia.org/wikipedia/commons/9/96/Num%C3%A9ro_2.jpg", className="steps"),
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
                html.Img(src="https://upload.wikimedia.org/wikipedia/commons/5/52/Num%C3%A9ro_3.jpg", className="steps"),
                html.Br(),
                html.Label("Data to put in the URI"),
                html.Div(children=[
                    html.Label("Year"), html.Br(),
                    dcc.Input(id="year", name="year", type="text", value="2020", debounce=True)
                ]),
                html.Div(children=[
                    html.Label("Project related"), html.Br(),
                    dcc.Input(id="project", name="project", type="text", value="aProject", debounce=True)
                ]),
                html.Div(children=[
                    html.Label("Related plant column"), html.Br(),
                    dcc.Input(id="relPlant", name="relPlant", type="text", value="Related_plant", debounce=True)
                ]),
                html.Div(children=[
                    html.Label("Species column"), html.Br(),
                    dcc.Input(id="species", name="species", type="text", value="Species", debounce=True)
                ])
            ])

def download_uri():
    return html.Div(children=[
        html.Button('Generate URI', id='generate_URI', className="button btn-default", n_clicks=0 )
    ])

def parse_contents(contents, filename, date):
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        try:
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                # ici des arguments pour skiprow et sep
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

        return  html.Div([
                html.H5(filename),
                html.H6(datetime.datetime.fromtimestamp(date)),

                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    page_size=10
                ),

                html.Hr(),  # horizontal line

                # For debugging, display the raw contents provided by the web browser
                html.Div('Raw Content'),
                html.Pre(contents[0:200] + '...', style={
                    'whiteSpace': 'pre-wrap',
                    'wordBreak': 'break-all'
                })
        ])

def URIgenerator_series(host, installation, resource_type, year="", lastvalue = "001", project="", datasup = {} ):
    if host[-1] != "/":
        host = host + "/" # Ensure host url ends with a slash
    finalURI = host + installation + "/"

    if resource_type == "agent":
        finalURI = finalURI + "id/agent/" + datasup["agentName"]
    
    if resource_type == "annotation":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/annotation/"+ year + "/" + Hash

    if resource_type == "actuator":
        finalURI = finalURI + year + "/a" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "document":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "documents/document" + Hash

    if resource_type == "data":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/data/" + Hash
    
    if resource_type == "ear":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/ea" + year[2:]+ str(lastvalue).rjust(6, "0") 

    if resource_type == "event":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + "id/event/" + year + "/" + Hash

    if resource_type == "image":
        Hash = hashlib.sha224(str(random.random()).encode("utf-8")).hexdigest()
        finalURI = finalURI + year + "/image/" + Hash

    if resource_type == "plant":
        finalURI = finalURI + year + "/" + project + "/pl" + year[2:]+ str(lastvalue).rjust(6, "0")
     
    if resource_type == "plot":
        finalURI = finalURI + year + "/" + project + "/pt" + year[2:]+ str(lastvalue).rjust(6, "0")
    
    if resource_type == "pot":
        finalURI = finalURI + year + "/" + project + "/po" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "leaf":
        relPlant = datasup['relPlant']
        finalURI = finalURI + year + "/" + project + "/" + relPlant + "/lf" + year[2:]+ str(lastvalue).rjust(6, "0")

    if resource_type == "species":
        finalURI = finalURI + datasup['species']

    if resource_type == "sensor":
        finalURI = finalURI + year + "/se" + year[2:] + str(lastvalue).rjust(6, "0")
    
    if resource_type == "vector":
        finalURI = finalURI + year + "/ve" + year[2:] + str(lastvalue).rjust(6, "0")

    if resource_type == "existing":
        relPlant = datasup['identifier']
        finalURI = finalURI + relPlant

    return finalURI

def add_URI_col(data, host = "", installation="", resource_type = "", project ="", year = "2017", datasup ="" ):
    activeDB = user_collected_URI.query.filter_by(user = session['username'], type = resource_type).first()
    datURI = []
    if(resource_type in ['plant', 'plot', 'pot', 'sensor', 'vector', 'actuator']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant)))
            lastplant +=1
        activeDB.lastvalue = str(lastplant)
        db.session.commit()
    if(resource_type in ['leaf', 'ear']):
        lastplant = int(activeDB.lastvalue)
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, project = project, lastvalue = str(lastplant), datasup = {'relPlant':data.eval(datasup)[l]}))
            lastplant +=1
        activeDB.lastvalue = str(lastplant)
        db.session.commit()

    if(resource_type in ['data', 'image', 'event', 'annotation']): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type))

    if(resource_type =="species"): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, year = year, resource_type = resource_type, datasup = {'species':data.eval(datasup)[l]}))

    if(resource_type =="existing"): 
        for l in range(0,len(data)):
            datURI.append(URIgenerator_series(host = host, installation = installation, resource_type = resource_type, datasup = {'identifier':data.eval(datasup)[l]}))
    data.insert(loc=0, column='URI' , value=datURI)
    return data
