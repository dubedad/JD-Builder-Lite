"""Flask application entry point for JD Builder Lite."""

from flask import Flask, render_template
from flask_cors import CORS
from src.routes.api import api_bp
from src.routes.careers import careers_bp
from src.config import SECRET_KEY, JOBFORGE_BRONZE_PATH
from src.vocabulary import VocabularyIndex, start_vocabulary_watcher
from src.services.generation_service import GenerationService, get_generation_service

# Module-level vocabulary state
vocab_index = None
vocab_observer = None

# Module-level generation service state
generation_service = None


def initialize_vocabulary():
    """Initialize vocabulary index and file watcher.

    Loads NOC vocabulary from JobForge parquet files and starts
    file watcher for automatic hot-reload on changes.
    Logs a warning and continues if parquet files are unavailable
    (e.g. running careers-only without full JobForge bronze layer).
    """
    global vocab_index, vocab_observer, generation_service

    try:
        vocab_index = VocabularyIndex(JOBFORGE_BRONZE_PATH)
        vocab_observer = start_vocabulary_watcher(vocab_index, JOBFORGE_BRONZE_PATH)
        print(f"[Vocabulary] Loaded: {vocab_index.get_term_count()} terms")
        generation_service = get_generation_service(vocab_index)
        print("[Generation] Service initialized (lazy loading enabled)")
    except FileNotFoundError as e:
        print(f"[Vocabulary] WARNING: {e}")
        print("[Vocabulary] JD Builder search features unavailable — careers site will still work.")


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

    # Initialize vocabulary index and watcher
    initialize_vocabulary()

    # Disable caching for static files in development
    @app.after_request
    def add_header(response):
        if app.debug:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(careers_bp)

    # Step 0 — routing gate
    @app.route('/')
    def landing():
        return render_template('landing.html')

    # JD Builder surface
    @app.route('/builder/')
    def index():
        return render_template('index.html')

    return app


# Module-level app for WSGI servers (gunicorn, etc.)
app = create_app()


if __name__ == '__main__':
    # Direct execution for development
    app = create_app()
    app.run(debug=True, port=5000)
