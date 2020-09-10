"""Routes for parent Flask app."""
from flask import render_template, Flask, session, url_for, request, redirect, jsonify, send_file, send_from_directory, flash, make_response
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
import random
import os

db = SQLAlchemy(app)

dir_path = os.path.dirname(os.path.realpath(__file__))

class user_collected_URI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    lastvalue = db.Column(db.String(200), nullable=False, default=1)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    #to avoid storage of clear text password
    password_hash =db.Column(db.String)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Routes
@app.route('/home')
@app.route('/')
def home():
    """Landing page."""

    if 'logged_in' not in session:
        session['logged_in']=False
    if 'username' in session:
        return render_template('index.jinja2', username = session['username'], statut = session['logged_in'],
        title='URI generator',
        description='App to generate URI for your data.',
        template='home-template',
        body="Generate URI for scientific data from a csv file and recolt the csv back.")
    else:
        session['username']=""
        return render_template('index.jinja2', username = "", statut = session['logged_in'],
        title='URI generator',
        description='App to generate URI for your data.',
        template='home-template',
        body="Generate URI for scientific data from a csv file and recolt the csv back.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['username'] = request.form['username']
        session['logged_in'] = True
        return redirect(url_for('home'))
    return render_template("login.html", 
        statut = session['logged_in'],
        template='home-template')

@app.route("/new_user", methods=['GET', 'POST'])
def create_user():
    if request.method=='POST':
        new_user = User(username = request.form['user'])
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        # init dbs
        init0=user_collected_URI(user = request.form['user'], type="actuator")
        init1=user_collected_URI(user = request.form['user'], type="plant")
        init2=user_collected_URI(user = request.form['user'], type="plot")
        init3=user_collected_URI(user = request.form['user'], type="pot")
        init4=user_collected_URI(user = request.form['user'], type="ear")
        init5=user_collected_URI(user = request.form['user'], type="leaf")
        init6=user_collected_URI(user = request.form['user'], type="sensor")
        init7=user_collected_URI(user = request.form['user'], type="vector")
        db.session.add(init0)
        db.session.add(init1)
        db.session.add(init2)
        db.session.add(init3)
        db.session.add(init4)
        db.session.add(init5)
        db.session.add(init6)
        db.session.add(init7)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('new_user.html', template='home-template')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))

@app.route("/get_started")
def get_started():
    return render_template("get_started.html", 
    username = session['username'],  
    statut = session['logged_in'],
    template='home-template')


### Fonctions
# @app.route("/import_dataset", methods = ['GET', 'POST'])
# def import_dataset():
#     if request.method == 'POST':
#         if not (session['logged_in']):
#             flash('You need to be connected to use this functionnality')
#             return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  

#         session['hostname'] = request.form['hostname']
#         session['installation'] = request.form['installation']  
#         if 'sep' in request.form:
#             SepSetting=request.form.get('sep')
#         else:
#             SepSetting=","
#         if 'skiprow' in request.form:
#             skipSetting=int(request.form['skiprow'])
#         else: 
#             skipSetting=0
#         f = request.files['file']
#         f.save(os.path.join(dir_path ,'uploads','uploaded_file.csv'))
#         try:
#           dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
#         except pd.errors.EmptyDataError:
#           flash("Invalid file, did you submit a csv file ?")
#           return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
#         dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)

#         if request.form.get('resource_type') in ['leaf', 'ear']:
#             try:
#                 dataset.eval(request.form['relplant'])
#             except pd.core.computation.ops.UndefinedVariableError:
#                 flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
#                 return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
#             dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'], datasup = request.form['relplant'])
        
#         if request.form.get('resource_type') == "species":
#             try:
#                 dataset.eval(request.form['species'])
#             except pd.core.computation.ops.UndefinedVariableError:
#                 flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
#                 return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'])  
#             dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , datasup = request.form['species'])  
        
#         if request.form.get('resource_type') in ['plant', 'pot', 'plot']:
#             dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , project = request.form['project'], year = request.form['year'])
        
#         if request.form.get('resource_type') in ['sensor', 'vector', 'data', 'image', 'event', 'annotation','actuator']:
#             dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = request.form.get('resource_type') , year = request.form['year'])
        
#         dataset_URI.to_csv(os.path.join(dir_path,'uploads','export_URI'+request.form.get('resource_type') +'.csv'))
#         return  send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI'+request.form['resource_type']  +'.csv'), mimetype="text/csv", as_attachment=True)

#         # response = send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI'+request.form['resource_type']  +'.csv'), mimetype="text/csv", as_attachment=True)
#         # response.headers['application'] = 'text/csv'
#         # return response
#     else:
#         if 'installation' in session:
#             return render_template("import.html", username = session['username'], installation = session['installation'], statut = session['logged_in'],
#     template='home-template')    
#         else:
#             return render_template("import.html", username = session['username'], installation = 'your installation', statut = session['logged_in'],
#     template='home-template')    

# @app.route('/existing_ID', methods = ['GET', 'POST'])
# def existing_id():
#     if request.method == 'POST':
#         if not (session['logged_in']):
#             flash('You need to be connected to use this functionnality')
#             return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 

#         session['hostname'] = request.form['hostname']
#         session['installation'] = request.form['installation']  
#         if 'sep' in request.form:
#             SepSetting=request.form.get('sep')
#         else:
#             SepSetting=","
#         if 'skiprow' in request.form:
#             skipSetting=int(request.form['skiprow'])
#         else: 
#             skipSetting=0
#         f = request.files['file']
#         f.save(os.path.join(dir_path,'uploads','uploaded_file.csv'))
#         try:
#           dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
#         except pd.errors.EmptyDataError:
#           flash("Invalid file, did you submit a csv file ?")
#           return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 
#         dataset = pd.read_csv(os.path.join(dir_path,'uploads','uploaded_file.csv'), sep=SepSetting, skiprows=skipSetting)
#         try:
#             dataset.eval(request.form['identifier'])
#         except pd.core.computation.ops.UndefinedVariableError:
#           flash("Invalid column name, or invalid field separator, verify that comma (,) is used to delimit cells, or specify the separatr in the 'Detail' section")
#           return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in']) 
#         dataset_URI = add_URI_col(data=dataset, host = session['hostname'], installation=session['installation'], resource_type = "existing" , datasup = request.form['identifier'])
#         dataset_URI.to_csv(os.path.join(dir_path,'uploads','export_URI_existing_ID.csv'))
#         return send_from_directory(directory=dir_path, filename=os.path.join('uploads','export_URI_existing_ID.csv'), mimetype="text/csv", as_attachment=True)
#     else:
#         if 'installation' in session:
#             return render_template("existing.html", username = session['username'], installation = session['installation'], statut = session['logged_in'],
#     template='home-template')  
#         else:
#             return render_template("existing.html", username = session['username'], installation = 'your installation', statut = session['logged_in'],
#     template='home-template')    


### Actions
@app.route("/your_database")
def your_database():
    collections = user_collected_URI.query.filter_by(user = session['username'])
    return render_template("your_database.html", 
    collections=collections, 
    username = session['username'], 
    statut = session['logged_in'],
    template='home-template')
