from flask import Flask


def create_app():
    app = Flask(__name__)
    with app.app_context():
        # Import the routes blueprint and register it with the app
        from .routes import bp as main_bp
        app.register_blueprint(main_bp)
    return app
