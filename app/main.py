"""Flask application factory."""

import logging
import sys
from flask import Flask
from app.config import get_config
from app.database import init_db
from app.routes import main_bp
from app.middleware import setup_request_logging, setup_error_handlers
from app.llm_service import LLMService


def create_app(config=None):
    """
    Application factory for creating and configuring the Flask app.

    Args:
        config: Optional configuration object. Defaults to environment-based config.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())

    # Setup logging
    _configure_logging(app.config.get("LOG_LEVEL", "INFO"))

    logger = logging.getLogger(__name__)
    logger.info(
        f"Starting DevOps LLM App v1.0.0 | env={app.config.get('FLASK_ENV', 'development')}"
    )

    # Initialize database
    init_db()

    # Initialize LLM service
    try:
        llm_service = LLMService(
            api_key=app.config["GROQ_API_KEY"],
            base_url=app.config["GROQ_BASE_URL"],
            model=app.config["GROQ_MODEL"],
            max_tokens=app.config["GROQ_MAX_TOKENS"],
            temperature=app.config["GROQ_TEMPERATURE"],
        )
        app.config["LLM_SERVICE"] = llm_service
        logger.info(f"LLM service initialized | model={app.config['GROQ_MODEL']}")
    except ValueError as e:
        logger.warning(f"LLM service not initialized: {e}")
        app.config["LLM_SERVICE"] = None

    # Register blueprints
    app.register_blueprint(main_bp)

    # Setup middleware
    setup_request_logging(app)
    setup_error_handlers(app)

    return app


def _configure_logging(level: str):
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
