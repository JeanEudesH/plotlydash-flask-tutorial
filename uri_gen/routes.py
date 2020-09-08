"""Routes for parent Flask app."""
from flask import render_template
from flask import current_app as app


@app.route('/')
def home():
    """Landing page."""
    return render_template(
        'home.html',
        title='URI generator',
        description='App to generate URI for your data.',
        template='home-template',
        body="Generate URI for scientific data from a csv file and recolt the csv back."
    )
