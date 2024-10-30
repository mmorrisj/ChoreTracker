from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Register CLI commands with app context
    with app.app_context():
        from . import cli  # Import CLI functions to register them

    return app