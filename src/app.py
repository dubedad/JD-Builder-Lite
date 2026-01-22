"""Flask application entry point for JD Builder Lite."""

from flask import Flask, render_template
from flask_cors import CORS
from src.routes.api import api_bp


def create_app():
    """Create and configure the Flask application.

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Enable CORS for frontend cross-origin requests
    CORS(app)

    # Register API blueprint
    app.register_blueprint(api_bp)

    # Root route to serve the frontend
    @app.route('/')
    def index():
        return render_template('index.html')

    return app


# Module-level app for WSGI servers (gunicorn, etc.)
app = create_app()


if __name__ == '__main__':
    # Direct execution for development
    app = create_app()
    app.run(debug=True, port=5000)
