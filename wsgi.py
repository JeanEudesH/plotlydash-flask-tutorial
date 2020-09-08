"""Application entry point."""
from uri_gen import init_app
from uri_gen import init_db

app = init_app()
db = init_db()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
