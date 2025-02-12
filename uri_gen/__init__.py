"""Initialize Flask app."""
from flask import Flask
from flask_assets import Environment

def init_app():
    """Construct core Flask application with embedded Dash app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///URI_database.db'
    assets = Environment()
    assets.init_app(app)

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes
        from .assets import compile_static_assets

        # Import Dash application
        from .plotlydash.dashboard import init_dashboard
        from .plotlydash.existing_id import init_dashboard2
        app = init_dashboard(app)
        app = init_dashboard2(app)
        # Compile static assets
        compile_static_assets(assets)

        return app