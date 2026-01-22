"""Flask application entry point for JD Builder Lite."""

from flask import Flask, render_template
from flask_cors import CORS
from src.routes.api import api_bp
from src.config import SECRET_KEY


def create_app():
    """Create and configure the Flask application.

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Add secret key for session support
    app.secret_key = SECRET_KEY

    # Enable CORS for frontend cross-origin requests
    CORS(app)

    # Disable caching for static files in development
    @app.after_request
    def add_header(response):
        if app.debug:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

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
