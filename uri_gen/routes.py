"""Routes for parent Flask app."""
from flask import render_template, Flask, session, url_for, request, redirect, jsonify, send_file, send_from_directory, flash, make_response
from flask import current_app as app

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

    # return render_template(
    #     'index.jinja2',
    #     title='URI generator',
    #     description='App to generate URI for your data.',
    #     template='home-template',
    #     body="Generate URI for scientific data from a csv file and recolt the csv back."
    # )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return render_template("login.html", statut = session['logged_in'])
        session['username'] = request.form['username']
        session['logged_in'] = True
        return render_template('home.html', username = session['username'], statut = session['logged_in'])
    return render_template("login.html", statut = session['logged_in'])

app.route("/new_user", methods=['GET', 'POST'])
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
        return render_template("login.html", statut = session['logged_in'])
    else:
        return render_template('new_user.html')

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
